### Foobar

Foobar is an example project that can run with the pyblish-magenta toolkit

##### Directory Layout

(dev: workspace-oriented; published: asset-oriented)

The development side is workspace oriented. A workspace can be defined as a department or stage in production, for example: Modeling, Animation, LookDev, Rigging, Lighting, Compositing, etc.

The published/asset side is asset oriented. An asset can be either a model (or collection of models) or a shot/sequence.

Here are some examples from dev:

Per-Model

- {project}/dev/modeling/characters/heroChar/maya
- {project}/dev/modeling/characters/heroChar/data/obj (not in there now for simplicity)
- {project}/dev/rigging/characters/heroChar/maya
- {project}/dev/lookDev/characters/heroChar/maya
- {project}/dev/lookDev/characters/heroChar/photoshop (not in there now for simplicity)

Per-Shot

- {project}/dev/animation/s01e01/sq010_sh010_aroundCorner
- {project}/dev/animation/s01e01/sq010_sh020_heroCU
- {project}/dev/animation/s01e01/sq010_sh020_heroCU
- {project}/dev/fx/s01e01/sq010_sh020_heroCU/houdini (not in there now for simplicity)
- {project}/dev/fx/s01e01/sq010_sh020_heroCU/maya

And some examples from asset:

Per-Model

- {project}/asset/model/characters/heroChar/model
- {project}/asset/model/characters/heroChar/rig
- {project}/asset/model/characters/heroChar/shaders
- {project}/asset/model/characters/heroChar/textures

Per-Shot

- {project}/asset/shots/s01e01/animation/sq010_sh010_aroundCorner/caches
- {project}/asset/shots/s01e01/animation/sq010_sh010_aroundCorner/cameras
- {project}/asset/shots/s01e01/animation/sq010_sh010_aroundCorner/scenes (not in there now for simplicity)
- {project}/asset/shots/s01e01/animation/sq010_sh010_aroundCorner/cameras
- {project}/asset/shots/s01e01/animation/sq010_sh010_aroundCorner/scenes (not in there now for simplicity)
- {project}/asset/renders/s01e01/edit (not in there now for simplicity)
- {project}/asset/renders/s01e01/maya/sq010_sh010_aroundCorner (not in there now for simplicity)
- {project}/asset/renders/s01e01/comp/sq010_sh010_aroundCorner (not in there now for simplicity)
- {project}/asset/renders/s01e01/playblast/sq010_sh010_aroundCorner (not in there now for simplicity)

Pros

- Development and published assets are completely separate (project/dev vs project/asset)
  - One of the original concepts whas that you should be able to back up a full 'final' version of a project by only transferring the assets folder. (Though this ended up being invalid as we've had separate resources repositories) Next iteration should improve on this.
- The development side being workspace oriented allows bigger studios to keep departments completely separate (rigging won't touch modeling).
- For the artist it's easy to understand where they should be working for a specific task (eg. Animation or Modeling)

Cons

- Hard for newcomers to see how the workspace data gets reformed into the asset oriented space and know where it ends up.
- Sometimes the asset oriented structure is nested in a (to newcomers) confusing manner, eg. {project}/asset/shots/{parentHierarchy}/animation/{assetName}
