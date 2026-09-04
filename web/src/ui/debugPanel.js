import GUI from "lil-gui";

/**
 * Dev-only shadow/lighting tuning panel. Imported only behind
 * `import.meta.env.DEV` in main.js so Vite excludes it (and the lil-gui
 * dependency) from the production bundle entirely.
 */
export function mountDebugPanel({ ambient, lights }) {
  const gui = new GUI({ title: "shadow tuning (dev only)" });

  gui.add(ambient, "intensity", 0, 2, 0.01).name("ambient intensity");

  for (const [name, light] of Object.entries(lights)) {
    const folder = gui.addFolder(name);
    folder.add(light, "intensity", 0, 10, 0.1);
    folder.add(light.shadow, "bias", -0.01, 0.01, 0.0001);
    folder.add(light.shadow, "normalBias", 0, 0.5, 0.005);
    folder
      .add(light.shadow.camera, "near", 1, light.shadow.camera.far - 1, 1)
      .onChange(() => light.shadow.camera.updateProjectionMatrix());
    folder
      .add(light.shadow.camera, "far", light.shadow.camera.near + 1, 300, 1)
      .onChange(() => light.shadow.camera.updateProjectionMatrix());
  }

  return gui;
}
