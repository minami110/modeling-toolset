import hou
import viewerstate.utils as su

HUD_TEMPLATE = {
    "title": "Snake Hook",
    "desc": "tool",
    "icon": "opdef:/minami110::Sop/snake_hook::2.0?snake_fook.png",
    "rows": [
        {"id": "width", "label": "Cross Section Width", "key": "LMB"},
        {"id": "height", "label": "Cross Section Height", "key": "Shift LMB"},
        {"id": "roll", "label": "Roll", "key": "Ctrl LMB"},
        {"id": "div", "label": "Cross Section Division", "key": "mousewheel"},
    ],
}


class State(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer
        self.scene_viewer.hudInfo(template=HUD_TEMPLATE)

    def onEnter(self, kwargs):
        node = kwargs["node"]
        state_parms = kwargs["state_parms"]
        node.setOutputForViewFlag(-1)  # Set view node in state

        # Store parameters
        self._parm_cross_width = node.parm("generate_cross_width")
        self._parm_cross_height = node.parm("crossHeightScale")
        self._parm_roll = node.parm("sweep1_roll")

    def onExit(self, kwargs):
        node = kwargs["node"]
        state_parms = kwargs["state_parms"]
        node.setOutputForViewFlag(0)  # Reset view node in state

    def onMouseEvent(self, kwargs):
        ui_event: hou.ViewerEvent = kwargs["ui_event"]
        device = ui_event.device()
        reason = ui_event.reason()

        # Release LMB
        if device.isLeftButtonReleased():
            self.scene_viewer.endStateUndo()
            return

        if not device.isLeftButton():
            return

        # Pressed LMB
        if reason == hou.uiEventReason.Start:
            self._mouse_x_pressed = device.mouseX()  # Cache mouse X screen positon
            self._lmb_pressed_ray_origin, _ = ui_event.ray()
            self._drag_scale = -1.0

            if device.isShiftKey():
                self._start_value_lmbop = self._parm_cross_height.eval()
                self._lmb_mode = 1  # height
                self.scene_viewer.beginStateUndo("Change cross section height")
            elif device.isCtrlKey():
                self._start_value_lmbop = self._parm_roll.eval()
                self._lmb_mode = 2  # roll
                self.scene_viewer.beginStateUndo("Change roll")
            else:
                self._start_value_lmbop = self._parm_cross_width.eval()
                self._lmb_mode = 0  # width
                self.scene_viewer.beginStateUndo("Change cross section width")

        # Dragging LMB
        elif reason == hou.uiEventReason.Active:
            delta_x = device.mouseX() - self._mouse_x_pressed

            if delta_x == 0.0:
                return

            if self._drag_scale < 0.0:
                origin, _ = ui_event.ray()
                origin_len: float = (self._lmb_pressed_ray_origin - origin).length()
                self._drag_scale = origin_len / abs(delta_x)

            # カメラの距離に応じてパラメーターしろを調整する
            if self._lmb_mode == 0:
                self._parm_cross_width.set(
                    max(self._start_value_lmbop + delta_x * self._drag_scale * 50, 0)
                )
            elif self._lmb_mode == 1:
                self._parm_cross_height.set(
                    max(self._start_value_lmbop + delta_x * self._drag_scale * 50, 0)
                )
            elif self._lmb_mode == 2:
                # Roll はカメラ距離に依存しない調整を行う5
                self._parm_roll.set(self._start_value_lmbop + delta_x * 0.8)

    def onMouseWheelEvent(self, kwargs):
        # Get mouse scroll (Up: 1 / Down: -1)
        device = kwargs["ui_event"].device()
        scroll = device.mouseWheel()

        # Increment or decrement count parameter
        node = kwargs["node"]
        parm_count = node.parm("halfcrosscount")
        currentcount = parm_count.eval()
        newcount = max(currentcount + scroll, 1)
        if newcount != currentcount:
            parm_count.set(newcount)


def createViewerStateTemplate():
    """Mandatory entry point to create and return the viewer state
    template to register."""

    state_typename = "minami110_snake_hook"
    state_label = "Snake Hook"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon("opdef:/minami110::Sop/snake_hook::2.0?snake_fook.png")

    return template
