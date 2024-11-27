from DiscretePlanning.Animators.AbstractAnimator import AbstractAnimator
from DiscretePlanning.Environments import HillClimber
from pathlib import Path
from plotly import graph_objects as go
import numpy as np
from ast import literal_eval
from typing import Dict
from json import loads
from moviepy.editor import ImageSequenceClip
import threading

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import  to_rgb
class HillClimberPlotlyAnimator(AbstractAnimator):
    def __init__(self, logFiles_dir: Path, styles_dir: Path, env : HillClimber, thread_num : int=1, print_option=True):
        super().__init__(logFiles_dir)
        self.style = loads(styles_dir.read_text())
        self._validateStyleSheet(styles_dir)

        self.print_option = print_option
        self.threads = thread_num
        self.progress_lock = threading.Lock()
        self.progress = 0

        self.initial_state = env.problem.initialState
        self.goalStates = env.problem.goalStates
        self.size = env.size
        self.height_function = env.height_function

        self.frames = []
        self.data = []
        self.fig = go.Figure()

    def _validateStyleSheet(self, styles_dir: Path):
        required_keys= {
            #these are just the keys directly accessed other options might still be necessary
            "mesh": None,
            "visitation scatter": {"marker": {"color": None}},
            "new state color": None,
            "initial state color": None,
            "goal state color": None,
            "solution path": None,
            "png layout": None,
            "png dimensions": None,
            'gif options': {"fps": None},
            "mp4 options": {"fps": None}
        }

        def _subvalidate(assessed_dict: Dict, req_dict: Dict, path='styleSheet'):
            for key, value in req_dict.items():
                current_path = f'{path}->[{key}]' if path else key
                if key not in assessed_dict:
                    raise KeyError(f"Required key '{current_path}' not found in style sheet.")
                if value is not None and isinstance(value, dict):
                    _subvalidate(assessed_dict[key], value, current_path)
        _subvalidate(self.style, required_keys)

    def setup_animation(self):
        # Generating Mesh
        x = np.arange(0, self.size[0], 1)
        y = np.arange(0, self.size[1], 1)
        x, y = np.meshgrid(x, y)
        z = np.vectorize(self.height_function)(x, y)

        #Generating data for go.Figure
        self.mesh = go.Surface(x=x, y=y, z=z, contours={
                                   "x": {'end': self.size[0],**self.style["contours"]},
                                   'y': {'end': self.size[1],**self.style["contours"]},
                               }, **self.style["mesh"])
        # Initially empty scatter plots
        self.scatter = go.Scatter3d(x=[], y=[], z=[], **self.style["visitation scatter"])
        self.goalScatter = go.Scatter3d(x=[], y=[], z=[], **self.style["visitation scatter"])

        self.data = [self.mesh, self.scatter, self.goalScatter]

        #Assigning Event Callbacks
        callbacks_calls =  [
            (
                {"Successor Not Previously Visited, Added to Memory"},
                self.generate_visitation_frame,
                "Generate Visitation Frame"
            ),
            (
                {"Solution Generated"},
                self.generate_solution_frame,
                "Generate Solution Frame"
            )
        ]
        for callSet, callback, name in callbacks_calls:
            self.subscribe_to_event(callSet, callback, name)

    def generate_visitation_frame(self, event: Dict):
        #generate visitation scatter points
        visited_states = event["Entry"]["Visitation Table"].keys()
        # Append elements of self.goalSet to visited_states
        visited_states_list = list(visited_states)
        for goalState in self.goalStates:
            visited_states_list.append(goalState)

        #build scatter plot coordinates
        points = map(literal_eval, visited_states_list)
        x, y = zip(*points)
        z = np.vectorize(self.height_function)(list(x), list(y))

        #color new state differently than other visited states
        specialPoint = (event["Entry"]["Successor"])

        #import colors from style sheet
        visitation_color, new_state_color = self.style["visitation scatter"]["marker"]["color"], self.style["new state color"]
        initial_state_color, goal_state_color = self.style['initial state color'], self.style['goal state color']

        colors = [visitation_color]*len(list(visited_states_list))
        for i, state in enumerate(visited_states_list):
            if state == specialPoint:
                colors[i] = new_state_color
            elif state in self.goalStates:
                colors[i]= goal_state_color
            elif state == self.initial_state:
                colors[i] = initial_state_color

        scatter_update = go.Scatter3d(x=x, y=y, z=z, **self.style["visitation scatter"])
        scatter_update.marker.color = colors

        # Keep mesh and goal scatter static, update only visitation scatter
        frame = go.Frame(data=[self.mesh, scatter_update, self.goalScatter], name=f"frame{len(self.frames)}")
        self.frames.append(frame)

    def generate_solution_frame(self, event: Dict):
        #generate solution points
        solution_string = event["Entry"]["Solution"]
        modified_solution_string = "[" + solution_string.replace(" -> ", ", ") + "]"
        solution_list = literal_eval(modified_solution_string)
        solution_list.reverse()
        solution_x, solution_y = zip(*solution_list)

        #generate visited points
        visited_states = event["Entry"]["Visitation Table"].keys()
        points = map(literal_eval, visited_states)
        x, y = zip(*points)
        z = np.vectorize(self.height_function)(list(x), list(y))
        visited_scatter_update = go.Scatter3d(x=x, y=y, z=z, **self.style["visitation scatter"])

        #generate animation building solution path
        generated_solution_list = []
        for sol_state in solution_list:
            generated_solution_list.append(sol_state)
            generated_solution_x, generated_solution_y = zip(*generated_solution_list)
            generated_solution_z = np.vectorize(self.height_function)(list(solution_x), list(solution_y))

            generated_goal_scatter_update = go.Scatter3d(
                x=generated_solution_x, y=generated_solution_y, z=generated_solution_z, **self.style["solution path"]
            )
            frame = go.Frame(data=[self.mesh, visited_scatter_update, generated_goal_scatter_update],
                             name=f"frame{len(self.frames)}")
            self.frames.append(frame)

    def save_frames_as_images(self, frames_dir: Path, num_threads: int = 4):
        if not frames_dir.exists():
            frames_dir.mkdir(parents=True, exist_ok=True)

        def save_frame_range(start_idx, end_idx, thread_id):
            for i in range(start_idx, end_idx):
                frame = self.fig.frames[i]
                frame_fig = go.Figure(data=frame.data, layout=self.fig.layout)
                frame_fig.update_layout(**self.style['png layout'])
                frame_fig.write_image(frames_dir / f"frame_{i:03d}.png", **self.style['png dimensions'])

                # Update progress
                if self.print_option:
                    with self.progress_lock:
                        self.progress += 1/len(self.frames)
                        print(f'Thread {thread_id}: Generating PNG of frame {i}, Completion: {self.progress:.3%}')

        total_frames = len(self.fig.frames)
        frames_per_thread = total_frames // num_threads
        threads = []

        for t in range(num_threads):
            start_idx = t * frames_per_thread
            end_idx = (t + 1) * frames_per_thread if t != num_threads - 1 else total_frames
            thread = threading.Thread(target=save_frame_range, args=(start_idx, end_idx, t))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def create_gif_from_images(self,frames_dir: Path, output_path: Path):
        # Get list of image files
        images = sorted([str(frame) for frame in frames_dir.glob("*.png")])

        # Create GIF
        clip = ImageSequenceClip(images, fps=self.style['gif options']['fps'])
        # Refined GIF creation options
        clip.write_gif(str(output_path), **self.style['gif options'])

    def create_mp4_from_images(self, frames_dir: Path, output_path: Path):
        images = sorted([str(frame) for frame in frames_dir.glob("*.png")])
        #create Image Sequence Clip
        duration_per_frame = 1 / self.style['mp4 options']['fps'] # or another desired duration
        clip = ImageSequenceClip(images, durations=[duration_per_frame] * len(images))
        #generate MP4
        clip.write_videofile(str(output_path), **self.style['mp4 options'])
        return

    def save_animation(self, save_dir: Path):
        self.fig = go.Figure(data=self.data, frames=self.frames)
        self.save_frames_as_images(save_dir.parent / "frames", self.threads)

        # Save and show the animation
        updatemenus = self.style["updatemenus"]
        sliders = [
            {
                **self.style["sliders"],
                "steps": [
                    {
                        "args": [[f"frame{k}"], {"frame": {"duration": 100, "redraw": True}, "mode": "immediate",
                                                 "transition": {"duration": 100}}],
                        "label": str(k),
                        "method": "animate"
                    } for k in range(len(self.frames))
                ]
            }
        ]
        self.fig.update_layout(updatemenus=updatemenus, sliders=sliders,
                               margin=self.style['png layout']['margin'],
                               showlegend=self.style['png layout']['showlegend'])
        self.fig.write_html(save_dir)
        # self.fig.show()

class HillClimberMatplotlibAnimator(AbstractAnimator):
    def __init__(self, logFiles_dir: Path, styles_dir: Path, env : HillClimber, print_option=True):
        super().__init__(logFiles_dir)
        #set up figure
        self.fig, self.ax = plt.subplots()
        self.print_option = print_option

        #set up dynamic Axes features
        self.visitation_scatter = self.ax.scatter([], [], [], c='grey', marker='o')

        #grab information from env
        self.initial_state = literal_eval(env.problem.initialState)
        self.goalStates = env.problem.goalStates
        self.size = env.size
        self.height_function = env.height_function

        self.frames = []

    def setup_animation(self):
        x, y = np.arange(0, self.size[0], 1), np.arange(0,self.size[1], 1)
        x, y = np.meshgrid(x, y)
        z = np.vectorize(self.height_function)(x, y)

        # the following elements are static in the animation so they are declared here
        # surface mesh
        self.ax.imshow(z , cmap='inferno', origin= 'lower')
        # initial state scatter
        self.ax.scatter(self.initial_state[0], self.initial_state[1], self.height_function(self.initial_state[0], self.initial_state[1]), c='r', marker='o', zorder =2)
        # goal state(s) scatter
        x_goal = [literal_eval(goal_state)[0] for goal_state in self.goalStates]
        y_goal = [literal_eval(goal_state)[1] for goal_state in self.goalStates]
        z_goal = [self.height_function(x_g, y_g) for x_g, y_g in zip(x_goal, y_goal)]
        self.ax.scatter(x_goal, y_goal, z_goal, c='r', marker='o', zorder = 2)

        #Assigning Callbacks
        callbacks_calls =  [
            (
                {"Successor Not Previously Visited, Added to Memory"},
                self.generate_visitation_frame,
                "Generate Visitation Frame"
            ),
            (
                {"Solution Generated"},
                self.generate_solution_frame,
                "Generate Solution Frame"
            )
        ]
        for callSet, callback, name in callbacks_calls:
            self.subscribe_to_event(callSet, callback, name)

    def generate_visitation_frame(self, event: Dict):
        # print(f'Visitation Frame Call on frame: {len(self.frames)}')
        visited_states = list(event["Entry"]["Visitation Table"].keys())
        visited_states = [literal_eval(state) for state in visited_states]
        # take transpose of visited states matrix to extract coordinates
        x, y = zip(*visited_states)
        x = list(x)
        y = list(y)
        z = np.vectorize(self.height_function)(x, y)

        # special point to be colored differently
        specialPoint = literal_eval(event["Entry"]["Successor"])
        colors = ['palegreen' if (x_pick,y_pick) == specialPoint else 'grey' for x_pick,y_pick in zip(x,y)]
        self.frames.append({'x': x, 'y': y, 'z': z, 'color': colors, 'name': 'generate_visitation_frame'})


    def generate_solution_frame(self, event: Dict):
        pass

    def _update(self, frame):
        # print("Update Function Called")
        if frame['name'] == "generate_visitation_frame":
            #remove old scatter plot
            self.visitation_scatter.remove()
            #plot new scatter plot
            self.visitation_scatter = self.ax.scatter(frame['x'], frame['y'], frame['z'] + 0.01, c=frame['color'],alpha=1, marker='o', zorder =3)
            return self.visitation_scatter,
        return
    def save_animation(self, save_dir: Path):
        # print("Log File Parsed Starting Matplotlib Animation")
        self.ani = FuncAnimation(fig=self.fig, func=self._update, frames=self.frames, interval=100, blit=True)
        # print("Saving Animation")
        self.ani.save(save_dir, writer='ffmpeg')
