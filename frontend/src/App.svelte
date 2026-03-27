<script>
  import { onMount } from "svelte";

  let config = {
    input_folder: "",
    output_folder: "",
    strategy: "highest",
    nth_image: 2,
    rename_prefix: "",
    limit_size: false,
    delete_subfolders: false,
  };

  let progress = { current: 0, total: 0 };
  let isProcessing = false;

  onMount(async () => {
    config = await eel.get_config()();
    eel.expose(update_progress, "update_progress");
    eel.expose(processing_complete, "processing_complete");
  });

  function update_progress(current, total) {
    progress = { current, total };
  }

  function processing_complete() {
    isProcessing = false;
    alert("Extraction complete!");
  }

  async function selectFolder(type) {
    const path = await eel.select_directory()();
    if (path) {
      if (type === "input") config.input_folder = path;
      if (type === "output") config.output_folder = path;
      eel.update_config(config)();
    }
  }

  function start() {
    isProcessing = true;
    progress = { current: 0, total: 0 };
    eel.start_processing(config)();
  }
</script>

<main>
  <h2>Image Extractor</h2>

  <section>
    <div class="row">
      <button on:click={() => selectFolder('input')}>Select Input Folder</button>
      <span>{config.input_folder || "No folder selected"}</span>
    </div>
    <div class="row">
      <button on:click={() => selectFolder('output')}>Select Output Folder</button>
      <span>{config.output_folder || "No folder selected"}</span>
    </div>
  </section>

  <section>
    <h3>Strategy</h3>
    <label>
      <input type="radio" bind:group={config.strategy} value="highest" />
      Extract Highest Confidence
    </label>
    <label>
      <input type="radio" bind:group={config.strategy} value="clean" />
      Extract clean.jpg
    </label>
    <label>
      <input type="radio" bind:group={config.strategy} value="nth" />
      Extract Every Nth Image
    </label>
    {#if config.strategy === 'nth'}
      <input type="number" bind:value={config.nth_image} min="1" style="width: 50px;" />
    {/if}
  </section>

  <section>
    <h3>Options</h3>
    <div class="row">
      <label>Rename Prefix:</label>
      <input type="text" bind:value={config.rename_prefix} />
    </div>
    <label>
      <input type="checkbox" bind:checked={config.limit_size} />
      Limit output folders to 1.9GB
    </label>
    <br/>
    <label>
      <input type="checkbox" bind:checked={config.delete_subfolders} />
      Delete original subfolders after extracting
    </label>
  </section>

  <button class="primary" on:click={start} disabled={isProcessing}>
    {isProcessing ? "Processing..." : "Start Extraction"}
  </button>

  {#if isProcessing || progress.total > 0}
    <div class="progress-container">
      <strong>Progress:</strong> {progress.current} / {progress.total} folders processed
    </div>
  {/if}
</main>

<style>
  main { font-family: system-ui; max-width: 700px; margin: 0 auto; padding: 20px; color: #333; }
  section { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ddd; }
  .row { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
  label { display: block; margin-bottom: 8px; cursor: pointer; }
  button { padding: 8px 16px; border-radius: 4px; border: 1px solid #ccc; background: #fff; cursor: pointer; }
  button:hover { background: #eef; }
  button.primary { background: #0066cc; color: white; border: none; font-size: 16px; width: 100%; padding: 12px; }
  button.primary:disabled { background: #999; cursor: not-allowed; }
  .progress-container { margin-top: 20px; padding: 15px; background: #e0f7fa; border-radius: 8px; text-align: center; }
</style>