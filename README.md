# modeling-toolset

## Install
```json
"MODELING_TOOLSET": "<ENTER_YOUR_INSTALL_PATH>/modeling-toolset"
```

- Open `modeling-toolset.json` and edit
- Copy `modeling-toolset.json` into `$HOUDINI_USER_PREF_DIR/packages/`
- See [Houdini packages](https://www.sidefx.com/docs/houdini/ref/plugins.html)

## SOPs
### Clone SOP
![](https://i.gyazo.com/0fbd0896f0c35089719f5a9db368d7e0.gif)

Copy input geometry on line. This tool inspired by MODO.  

### Radial Array SOP
![](https://i.gyazo.com/744c41f2fc0ef80e2431a95559c8353e.gif)

Copy input geometry on circle. This tool inspired by MODO.

### PolyFill from Points SOP
![](https://i.gyazo.com/610c87ddde41f57cd41181f8b800141f.gif)

[PolyFill SOP](https://www.sidefx.com/docs/houdini/nodes/sop/polyfill.html) does not supports point selection, this node supports point selection in addition to edge selection.  
This tool inspired by MODO.

### Snake Hook SOP
![](https://i.gyazo.com/9f719c796dbbbecd58233dfeff102352.gif)

This tool extends the [Sweep SOP](https://www.sidefx.com/docs/houdini/nodes/sop/sweep.html) so that the Cross Section can also be adjusted from the Ramp.
It used to create shapes such as nails and toon-look hair.
