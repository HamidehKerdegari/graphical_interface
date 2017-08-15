#!/usr/bin/env python
################################################################
import rospy
import interface_lib as lib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# ==============================================================

class MiroGI():
    def __init__(self):
        rospy.init_node("miro_ros_client_py", anonymous=True)
        self.miro = lib.miro_ros_client()

        img_back = plt.imread('../documents/biomimetic_core.png')
        self.img_caml = plt.imread('../documents/caml.png')
        self.img_camr = plt.imread('../documents/camr.png')


        # Initializing the main window.
        self.screen_size = [800, 450]
        self.fig_main, self.ax_main = plt.subplots(nrows=1, ncols=1, figsize=(9, 5))
        self.fig_main.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0, hspace=0.0)
        self.pltManager = plt.get_current_fig_manager()
        self.pltManager.resize(*self.pltManager.window.maxsize()) # Make full screen

        # Setting the back/static image(s).
        self.ax_main.imshow(img_back, zorder=0, aspect='auto', extent=[0, self.screen_size[0], 0, self.screen_size[1]])
        self.ax_main.axis('off')  # clear x- and y-axes
        self.ax_main.set_xlim([0, self.screen_size[0]])
        self.ax_main.set_ylim([0, self.screen_size[1]])


        # Initializing the GPR plot.
        self.ax_GPR = lib.add_subplot(self.ax_main, self.fig_main, [0.833, 0.695, 0.09, 0.084])
        self.index = np.arange(8)
        self.bar_width = 0.9
        self.opacity = 1.0
        for spine in plt.gca().spines.values():  # Get rid of the frame
            spine.set_visible(False)
        self.ax_GPR.patch.set_visible(False)  # Remove backgrounf
        self.ax_GPR.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off', labelbottom='on')
        self.ax_GPR.set_xticks(self.index + self.bar_width / 2)
        self.ax_GPR.set_xticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
        self.colors = ['tomato', 'darkcyan', 'paleturquoise', 'blueviolet', 'hotpink', 'seagreen', 'navy']
        self.plt_GPR_handle = self.ax_GPR.bar(self.index, (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0), self.bar_width, zorder=1, alpha=self.opacity, color=self.colors)


        #  Initializing moving circle.
        self.ax_circle = lib.add_subplot(self.ax_main, self.fig_main, [0.652, 0.43, 0.275*9.0/16.0, 0.275])
        for spine in plt.gca().spines.values():  # Get rid of the frame
            spine.set_visible(False)
        self.ax_circle.patch.set_visible(False)  # Remove backgrounf
        self.ax_circle.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off', labelbottom='off')
        self.ax_circle.set_xlim([-10, 10])
        self.ax_circle.set_ylim([-10, 10])
        self.ax_circle.set_aspect('auto')
        self.plt_circle_red_handle = self.ax_circle.scatter(2, 7, s=200, c='r', alpha=self.opacity, zorder=1)
        self.plt_circle_blue_handle = self.ax_circle.scatter(2, 7, s=200, c='b', alpha=self.opacity, zorder=1)
        self.plt_circle_yellow_handle = self.ax_circle.scatter(2, 7, s=200, c='y', alpha=self.opacity, zorder=1)

        #  Initializing camera left.
        self.ax_camera_l = lib.add_subplot(self.ax_main, self.fig_main, [0.27, 0.43, 0.15, 0.17])
        for spine in plt.gca().spines.values():  # Get rid of the frame
            spine.set_visible(False)
        self.ax_camera_l.patch.set_visible(False)  # Remove backgrounf
        self.ax_camera_l.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off', labelbottom='off')
        self.plt_camera_l_handle = self.ax_camera_l.imshow(self.img_caml, zorder=1, aspect='auto')

        #  Initializing camera right.
        self.ax_camera_r = lib.add_subplot(self.ax_main, self.fig_main, [0.36, 0.43, 0.15, 0.17])
        for spine in plt.gca().spines.values():  # Get rid of the frame
            spine.set_visible(False)
        self.ax_camera_r.patch.set_visible(False)  # Remove backgrounf
        self.ax_camera_r.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off',
                                     labelbottom='off')
        self.plt_camera_r_handle = self.ax_camera_r.imshow(self.img_camr, zorder=1, aspect='auto')

        # cursor = Cursor()
        cid = self.fig_main.canvas.mpl_connect('button_press_event', self.onclick)

        ani = animation.FuncAnimation(self.fig_main, self.plot_updatefig, interval=500)
        plt.show()

    def img_plot(self, ax, image, size, pos, zorder, ofset_centre=True):

        if ofset_centre:
            extent = [pos[0] - (size[0] / 2), pos[0] + (size[0] / 2), \
                      pos[1] - (size[1] / 2), pos[1] + (size[1] / 2) ]
        else:
            extent = [pos[0], pos[0] + size[0], pos[1], pos[1] + size[1]]

        img_handle = ax.imshow(image, zorder=zorder, extent=extent)
        return img_handle

    def plot_updatefig(self, i):
        if rospy.core.is_shutdown():
            return
        while (self.miro.platform_sensors is None) or (self.miro.core_state is None):
            pass
        self.miro.update_data()

        # Plotting animation
        self.plt_circle_red_handle.remove()
        self.plt_circle_blue_handle.remove()
        self.plt_circle_yellow_handle.remove()
        x = self.miro.accel_head.x
        y = self.miro.accel_head.y
        self.plt_circle_red_handle = self.ax_circle.scatter(self.miro.emotion.valence*16.0-8.0, self.miro.emotion.arousal*16.0-8.0, s=200, c='r', alpha=self.opacity, zorder=1)
        self.plt_circle_blue_handle = self.ax_circle.scatter(self.miro.mood.valence*16.0-8.0, self.miro.mood.arousal*16.0-8.0, s=200, c='b', alpha=self.opacity, zorder=1)
        self.plt_circle_yellow_handle = self.ax_circle.scatter(self.miro.sleep.wakefulness*16.0-8.0, self.miro.sleep.pressure*16.0-8.0, s=200, c='y', alpha=self.opacity, zorder=1)

        self.plt_GPR_handle.remove()
        self.plt_GPR_handle = self.ax_GPR.bar(self.index, self.miro.selection, self.bar_width, zorder=1, alpha=self.opacity, color=self.colors)

        self.plt_camera_l_handle.remove()
        self.plt_camera_l_handle = self.ax_camera_l.imshow(self.miro.image_caml, zorder=1, aspect='auto')

        self.plt_camera_r_handle.remove()
        self.plt_camera_r_handle = self.ax_camera_r.imshow(self.miro.image_camr, zorder=1, aspect='auto')


    # Getting the cursor click position.
    def onclick(self, event):
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              (event.button, event.x, event.y, event.xdata, event.ydata))

################################################################
if __name__ == "__main__":
    # Setting the back/static image(s).
    MainGI = MiroGI()

################################################################
