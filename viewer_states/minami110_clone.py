import hou
import viewerstate.utils as su


class CloneState(object):

    # Hotkeys and menus
    CONTEXT_MENU_NAME = "clone_menu"
    MENU_JUMPMODE_CODE = "enter_jump_mode"
    MENU_BETWEENMODE_CODE = "enter_between_mode"

    # parameter types
    MODE_PARM = "mode"
    COUNT_PARM = "count"

    class Mode:
        JUMP = 0
        BETWEEN = 1

    MODE_NAMES = ["Jump", "Between"]

    def __init__(self, state_name, scene_viewer):

        self.state_name = state_name
        self.scene_viewer = scene_viewer
        self.node = None

        category = hou.sopNodeTypeCategory()
        HK_CTXT = su.hotkeyContextForState(
            state_name, category
        )  # h.pane.gview.state.sop.minami110_clone

        def hkSymbol(code):
            return HK_CTXT + "." + code

        hk_jump_mode = hkSymbol(CloneState.MENU_JUMPMODE_CODE)
        hk_between_mode = hkSymbol(CloneState.MENU_BETWEENMODE_CODE)

        HUD_TEMPLATE = {
            "title": "Clone",
            "desc": "tool",
            "icon": "opdef:/minami110::Sop/clone::2.0?clone.png",
            "rows": [
                {
                    "id": "mode",
                    "label": "Mode",
                    "key": "{}/{}".format(
                        su.hudHotkeyRef(hk_jump_mode), su.hudHotkeyRef(hk_between_mode)
                    ),
                },
                {"id": "mode_g", "type": "choicegraph", "count": 2},
                {"id": "radius", "label": "Change count", "key": "mousewheel"},
            ],
        }

        self.scene_viewer.hudInfo(template=HUD_TEMPLATE)

    def onEnter(self, kwargs):
        self.node = kwargs["node"]
        self.node.addEventCallback(
            [hou.nodeEventType.ParmTupleChanged], self._nodeParmUpdated
        )
        self.node.addEventCallback(
            [hou.nodeEventType.InputRewired], self._inputRewired
        )
        self.node.setOutputForViewFlag(-1)
        self._updateHud()

        self._updateHandleOrigin()

        

    def onExit(self, kwargs):
        self.node.removeEventCallback(
            [hou.nodeEventType.ParmTupleChanged], self._nodeParmUpdated
        )
        self.node.removeEventCallback(
            [hou.nodeEventType.InputRewired], self._inputRewired
        )
        self.node.setOutputForViewFlag(0)

    def onMouseWheelEvent(self, kwargs):
        # Get mouse scroll (Up: 1 / Down: -1)
        device = kwargs["ui_event"].device()
        scroll = device.mouseWheel()

        # Increment or decrement count parameter
        parm_count = self.node.parm(CloneState.COUNT_PARM)
        currentcount = parm_count.evalAsInt()
        newcount = max(currentcount + scroll, 2)
        if newcount != currentcount:
            parm_count.set(newcount)

    # HotKey 押されたとき
    def onMenuAction(self, kwargs):
        item = kwargs["menu_item"]

        # mode parm を更新する
        if item == CloneState.MENU_JUMPMODE_CODE:
            self.node.parm(CloneState.MODE_PARM).set(CloneState.Mode.JUMP)
        elif item == CloneState.MENU_BETWEENMODE_CODE:
            self.node.parm(CloneState.MODE_PARM).set(CloneState.Mode.BETWEEN)

    def _updateHud(self):
        # mode に応じて HUD の見た目を更新する
        mode = self.node.parm(CloneState.MODE_PARM).evalAsInt()
        self.scene_viewer.hudInfo(
            values={
                "mode": CloneState.MODE_NAMES[mode],
                "mode_g": mode,
            }
        )

    # ノードのパラメータが更新されたときのコールバック
    def _nodeParmUpdated(self, event_type, node, **kwargs):
        parm_tuple = kwargs.get("parm_tuple")
        if not parm_tuple:
            return

        parm_name = parm_tuple.name()

        # mode が変更されたときは Hud を更新する
        if parm_name == CloneState.MODE_PARM:
            self._updateHud()

    def _inputRewired(self, event_type, node, **kwargs):
        self._updateHandleOrigin()

    def _updateHandleOrigin(self):
        # 入力Geometry にアクセスして, Bounding Box の Center を取得する
        # この値を Hidden している Handle 用のパラメーター origin に代入しておく
        geo = self.node.inputGeometry(0)

        if not geo:
            with hou.undos.disabler():
                self.node.parm("originx").set(0)
                self.node.parm("originy").set(0)
                self.node.parm("originz").set(0)
            return

        bBox = geo.boundingBox()
        center = bBox.center()
        with hou.undos.disabler():
            self.node.parm("originx").set(center.x())
            self.node.parm("originy").set(center.y())
            self.node.parm("originz").set(center.z())


def createViewerStateTemplate():
    """Mandatory entry point to create and return the viewer state
    template to register."""

    state_typename = "minami110_clone"
    state_label = "Clone"
    state_category = hou.sopNodeTypeCategory()
    state_icon = "opdef:/minami110::Sop/clone::2.0?clone.png"

    template = hou.ViewerStateTemplate(state_typename, state_label, state_category)
    template.bindFactory(CloneState)
    template.bindIcon(state_icon)

    # Begin Hotkey setup
    hotkey_definitions: hou.PluginHotkeyDefinitions = hou.PluginHotkeyDefinitions()
    menu = hou.ViewerStateMenu(CloneState.CONTEXT_MENU_NAME, "Clone Menu")

    def addHotkeyActionItem(code, desc, key):
        hk = su.defineHotkey(
            hotkey_definitions,
            state_typename,
            code,
            key,
            desc,
            state_cat=state_category,
        )
        menu.addActionItem(code, desc, hotkey=hk)

    addHotkeyActionItem(CloneState.MENU_JUMPMODE_CODE, "Enter Jump Mode", "1")
    addHotkeyActionItem(CloneState.MENU_BETWEENMODE_CODE, "Enter Between Mode", "2")

    template.bindMenu(menu)
    template.bindHotkeyDefinitions(hotkey_definitions)

    # End hotkey setup

    return template
