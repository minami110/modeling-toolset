import hou


class RadialArrayState(object):

    ICON = "minami110_radial_array"
    BEGIN_ANGLE_PARM = "beginangle"
    END_ANGLE_PARM = "endangle"
    OFFSET_PARM = "offset"
    COUNT_PARM = "count"

    class DragMode:
        END_ANGLE = 0
        BEGIN_ANGLE = 1
        OFFSET = 2

    def __init__(self, state_name: str, scene_viewer: hou.SceneViewer):

        self.state_name = state_name
        self.scene_viewer = scene_viewer

        HUD_TEMPLATE = {
            "title": "Radial Array",
            "desc": "tool",
            "icon": RadialArrayState.ICON,
            "rows": [
                {"id": "count", "label": "Count", "key": "mousewheel"},
                {"id": "endangle", "label": "End Angle", "key": "LMB"},
                {"id": "beginangle", "label": "Begin Angle", "key": "Shift LMB"},
                {"id": "offset", "label": "Offcet", "key": "Ctrl LMB"},
            ],
        }

        self.scene_viewer.hudInfo(template=HUD_TEMPLATE)

    def onEnter(self, kwargs):
        self.node: hou.SopNode = kwargs["node"]

    def onExit(self, kwargs):
        pass

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

            if device.isShiftKey():
                self._start_value_lmbop = self.node.parm(
                    RadialArrayState.BEGIN_ANGLE_PARM
                ).evalAsFloat()
                self._lmb_mode = RadialArrayState.DragMode.BEGIN_ANGLE
                self.scene_viewer.beginStateUndo("Change begin angle")
            elif device.isCtrlKey():
                self._start_value_lmbop = self.node.parm(
                    RadialArrayState.OFFSET_PARM
                ).evalAsFloat()
                self._lmb_mode = RadialArrayState.DragMode.OFFSET
                self.scene_viewer.beginStateUndo("Change offset")
            else:
                self._start_value_lmbop = self.node.parm(
                    RadialArrayState.END_ANGLE_PARM
                ).evalAsFloat()
                self._lmb_mode = RadialArrayState.DragMode.END_ANGLE
                self.scene_viewer.beginStateUndo("Change end angle")

        # Dragging LMB
        elif reason == hou.uiEventReason.Active:
            delta_x = device.mouseX() - self._mouse_x_pressed

            if delta_x == 0.0:
                return

            if self._lmb_mode == RadialArrayState.DragMode.END_ANGLE:
                self.node.parm(RadialArrayState.END_ANGLE_PARM).set(
                    self._start_value_lmbop + delta_x * 0.25
                )
            elif self._lmb_mode == RadialArrayState.DragMode.BEGIN_ANGLE:
                self.node.parm(RadialArrayState.BEGIN_ANGLE_PARM).set(
                    self._start_value_lmbop + delta_x * 0.25
                )
            elif self._lmb_mode == RadialArrayState.DragMode.OFFSET:
                self.node.parm(RadialArrayState.OFFSET_PARM).set(
                    self._start_value_lmbop + delta_x * 0.05
                )

    def onMouseWheelEvent(self, kwargs):
        # Get mouse scroll (Up: 1 / Down: -1)
        device = kwargs["ui_event"].device()
        scroll = device.mouseWheel()

        # Increment or decrement count parameter
        parm_count = self.node.parm(RadialArrayState.COUNT_PARM)
        currentcount = parm_count.evalAsInt()
        newcount = max(currentcount + scroll, 2)
        if newcount != currentcount:
            parm_count.set(newcount)


def createViewerStateTemplate():
    state_typename = "minami110_radial_array"
    state_label = "Radial Array"
    state_category = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_category)
    template.bindFactory(RadialArrayState)
    template.bindIcon(RadialArrayState.ICON)

    return template
