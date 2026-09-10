/**
 * Minimal three.js viewer for the device models: drag to orbit, scroll to
 * zoom, nothing else.
 *
 * This module is loaded by a dynamic import() the first time a reader
 * opens a model, never on page load. That is the whole reason the site's
 * only JavaScript dependency is affordable: three.js is a few hundred
 * kilobytes, and a visitor who never clicks a render never downloads a
 * byte of it. Keep every three.js import inside this file; importing it
 * from an .astro component's frontmatter or a top-level <script> would
 * pull it into the main bundle and defeat that.
 */
import {
  AmbientLight,
  Box3,
  Color,
  DirectionalLight,
  NoToneMapping,
  PerspectiveCamera,
  Scene,
  SRGBColorSpace,
  Vector3,
  WebGLRenderer,
} from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// Matches --bg-2 in global.css, so the canvas is indistinguishable from
// the card the static renders sit on. The renders themselves ship with a
// transparent background and are composited onto that same colour.
const BACKGROUND = 0xf6f7f9;

export function createViewer(container) {
  const renderer = new WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = SRGBColorSpace;
  // No tone mapping, deliberately: the same call the Blender scene makes
  // when it sets its view transform to "Standard" (see the comment in
  // tools/render_parts.py). A filmic curve rolls off highlights and
  // desaturates, which washed the parts' colours out toward pale cream
  // and near-white: the model stopped matching the render it was opened
  // from, which is the one thing this viewer must not do.
  renderer.toneMapping = NoToneMapping;
  container.appendChild(renderer.domElement);

  const scene = new Scene();
  scene.background = new Color(BACKGROUND);

  const camera = new PerspectiveCamera(35, 1, 0.001, 100);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  // Scroll zoom only bites once the pointer is over the canvas, and the
  // dialog is modal, so this cannot hijack the page's own scrolling.
  controls.zoomSpeed = 0.8;
  controls.rotateSpeed = 0.9;

  // The conventional CAD/three.js scheme, left at its defaults: left drag
  // orbits, right drag pans, middle drag and the wheel zoom. Panning was
  // switched off in the first version to stop a reader pushing the model
  // out of frame. That was the wrong trade, because it also removed the only way
  // to look at an off-centre feature up close. "Reset view" is the
  // recovery path instead.
  controls.enablePan = true;
  controls.screenSpacePanning = true;
  controls.panSpeed = 0.9;

  // Shift/Ctrl/Cmd + left-drag also pans. This is the trackpad escape hatch,
  // since a trackpad has no comfortable right-drag and its two-finger
  // drag is already spoken for (macOS reports that as a wheel event, so
  // it is the zoom). That modifier is OrbitControls' own behaviour once
  // enablePan is true, not something to add here: an earlier version
  // rebound mouseButtons.LEFT to PAN on shift-keydown, and the control's
  // internal "modifier held → swap rotate and pan" rule then inverted it
  // straight back to a rotate. Leave the bindings alone.

  // A three-point rig echoing the Blender scene's key/fill/rim, at
  // roughly its 4:1 key-to-fill ratio, so the model reads with the same
  // sense of form as the Cycles render even though this is real-time
  // shading rather than path tracing. Total incident light is kept near
  // 1.0 on a lit surface: with no tone mapping there is no highlight
  // rolloff to absorb over-lighting, so anything much above that clips
  // the base colours to white, which is exactly how the first attempt
  // (ambient 1.6 plus a 2.4 key) lost the palette.
  scene.add(new AmbientLight(0xffffff, 0.55));
  const key = new DirectionalLight(0xffffff, 1.45);
  key.position.set(0.6, 0.9, 0.8);
  scene.add(key);
  const fill = new DirectionalLight(0xffffff, 0.38);
  fill.position.set(-0.8, 0.4, 0.4);
  scene.add(fill);
  const rim = new DirectionalLight(0xffffff, 0.32);
  rim.position.set(0, 0.6, -0.9);
  scene.add(rim);

  let model = null;
  let running = false;

  function resize() {
    const { clientWidth: w, clientHeight: h } = container;
    if (!w || !h) return;
    // The third argument (updateStyle) must stay at its default `true`.
    // Passing `false` was a real bug on every HiDPI screen: setPixelRatio
    // makes the drawing buffer devicePixelRatio times larger, and with no
    // CSS size written, the canvas's width/height *attributes* become its
    // layout size, so on a 2x display an 898x558 stage held a canvas
    // laid out at 1796x1116 and only its top-left quarter was visible.
    // The model appeared jammed into a corner and the centre of rotation,
    // being the centre of the real canvas, sat off-screen. It looked
    // correct at 1x, which is exactly why it survived the first round of
    // testing; see the CSS in Device.astro for the belt-and-braces cap.
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }

  // Frame whatever was loaded from its own bounding sphere rather than
  // from hardcoded distances: the three models differ in size by more
  // than an order of magnitude (a whole exploded assembly vs a 37 mm
  // filter support), and their glTF units are millimetres-as-metres.
  function frame() {
    const box = new Box3().setFromObject(model);
    const size = box.getSize(new Vector3());
    const center = box.getCenter(new Vector3());
    const radius = size.length() / 2;

    model.position.sub(center);

    // Fit the bounding SPHERE, not the box: the sphere is the same size
    // from every angle, so a model framed this way stays inside the frame
    // through any orbit, which a box fit cannot promise.
    //
    // Both axes are checked. camera.fov is the *vertical* field of view,
    // so solving for it alone only fits a landscape stage; on a portrait
    // one (a phone) the horizontal field is the narrower of the two and
    // the model would have hung off the sides.
    const halfV = Math.tan((camera.fov * Math.PI) / 180 / 2);
    const halfH = halfV * camera.aspect;
    const distance = (radius * 1.15) / Math.min(halfV, halfH);

    camera.position.set(distance * 0.55, distance * 0.42, distance * 0.72);
    camera.near = radius / 100;
    camera.far = radius * 100;
    camera.updateProjectionMatrix();

    // The orbit pivot is the centre of that same sphere, which the model
    // was just translated onto, so rotation turns the geometry in place
    // rather than swinging it around some point off to one side.
    controls.target.set(0, 0, 0);
    // Bound the scroll so a reader cannot zoom through the geometry and
    // lose the model, nor zoom out until it is a speck. The near bound is
    // deliberately well inside the bounding sphere: the details worth
    // opening a 3D view for (the sealing ridge, the strand mesh) are
    // small features on a much larger part.
    controls.minDistance = radius * 0.3;
    controls.maxDistance = distance * 2.2;
    controls.update();
  }

  function tick() {
    if (!running) return;
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(tick);
  }

  const loader = new GLTFLoader();

  return {
    async load(url) {
      if (model) {
        scene.remove(model);
        model.traverse((o) => {
          if (o.isMesh) {
            o.geometry.dispose();
            const mats = Array.isArray(o.material) ? o.material : [o.material];
            mats.forEach((m) => m && m.dispose());
          }
        });
        model = null;
      }
      const gltf = await loader.loadAsync(url);
      model = gltf.scene;
      scene.add(model);
      resize();
      frame();
    },
    start() {
      if (running) return;
      running = true;
      resize();
      tick();
    },
    // Stopping the loop on close matters: a requestAnimationFrame loop
    // left running behind a closed dialog keeps a GPU context busy and
    // drains battery for as long as the page stays open.
    stop() {
      running = false;
    },
    resize,
    reset() {
      if (model) frame();
    },
  };
}
