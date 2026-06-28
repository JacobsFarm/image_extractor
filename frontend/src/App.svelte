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
    copy_files: false,
  };
  let progress = { current: 0, total: 0 };
  let isProcessing = false;
  let activeCategory = "data";

  onMount(async () => {
    config = await eel.get_config()();
    
    // Bepaal welke tab open moet staan op basis van de laatst opgeslagen configuratie
    if (['best', 'metadata', 'video'].includes(config.strategy)) {
      activeCategory = 'media';
    } else {
      activeCategory = 'data';
    }

    eel.expose(update_progress, "update_progress");
    eel.expose(processing_complete, "processing_complete");
    eel.expose(extraction_message, "extraction_message");
  });

  let lastMessage = "";

  function update_progress(current, total) {
    progress = { current, total };
  }

  function extraction_message(message) {
    lastMessage = message;
  }

  function processing_complete() {
    isProcessing = false;
    if (lastMessage) {
      alert(lastMessage);
    } else {
      alert("Extraction complete!");
    }
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
    lastMessage = "";
    progress = { current: 0, total: 0 };
    eel.start_processing(config)();
  }

  function setCategory(cat) {
    activeCategory = cat;
    // Zorg dat we automatisch een geldige optie selecteren bij het wisselen van tabblad
    if (cat === 'data' && !['highest', 'clean', 'nth'].includes(config.strategy)) {
      config.strategy = 'highest';
    } else if (cat === 'media' && !['best', 'metadata', 'video'].includes(config.strategy)) {
      config.strategy = 'best';
    }
  }
</script>

<main>
  <h2>Image Extractor</h2>

  <section>
    <div class="row">
      <button class="folder-btn" on:click={() => selectFolder('input')}>Select Input Folder</button>
      <span>{config.input_folder || "No folder selected"}</span>
    </div>
    <div class="row">
      <button class="folder-btn" on:click={() => selectFolder('output')}>Select Output Folder</button>
      <span>{config.output_folder || "No folder selected"}</span>
    </div>
  </section>

  <section>
    <div class="section-header">
      <h3>Strategy</h3>
      <div class="tabs">
        <button class="tab" class:active={activeCategory === 'data'} on:click={() => setCategory('data')}>Data</button>
        <button class="tab" class:active={activeCategory === 'media'} on:click={() => setCategory('media')}>Media</button>
      </div>
    </div>
    
    <div class="strategy-grid">
      {#if activeCategory === 'data'}
        <div class="strategy-column">
          <label class="box-label" class:selected={config.strategy === 'highest'}>
            <input type="radio" bind:group={config.strategy} value="highest" />
            Extract Highest Confidence
          </label>
          
          <label class="box-label" class:selected={config.strategy === 'clean'}>
            <input type="radio" bind:group={config.strategy} value="clean" />
            Extract clean.jpg
          </label>
          
          <label class="box-label" class:selected={config.strategy === 'nth'}>
            <input type="radio" bind:group={config.strategy} value="nth" />
            Extract Every Nth Image
          </label>
        </div>
      {/if}

      {#if activeCategory === 'media'}
        <div class="strategy-column">
          <label class="box-label" class:selected={config.strategy === 'best'}>
            <input type="radio" bind:group={config.strategy} value="best" />
            Extract best.jpg
          </label>
          
          <label class="box-label" class:selected={config.strategy === 'metadata'}>
            <input type="radio" bind:group={config.strategy} value="metadata" />
            Extract metadata.json
          </label>
          
          <label class="box-label" class:selected={config.strategy === 'video'}>
            <input type="radio" bind:group={config.strategy} value="video" />
            Extract video.mp4
          </label>
        </div>
      {/if}
    </div>

    {#if config.strategy === 'nth'}
      <div class="nth-input-container">
        <label for="nth-interval">Every Nth image interval:</label>
        <input id="nth-interval" type="number" bind:value={config.nth_image} min="1" style="width: 60px;" />
      </div>
    {/if}
  </section>

  <section>
    <h3>Options</h3>
    <div class="row">
      <label class="inline-label" for="rename-prefix">Rename Prefix:</label>
      <input id="rename-prefix" type="text" bind:value={config.rename_prefix} />
    </div>
    <label class="checkbox-label">
      <input type="checkbox" bind:checked={config.limit_size} />
      Limit output folders to 1.9GB
    </label>
    <label class="checkbox-label">
      <input type="checkbox" bind:checked={config.copy_files} />
      Copy files instead of moving them
    </label>
    <label class="checkbox-label" class:disabled={config.copy_files}>
      <input type="checkbox" bind:checked={config.delete_subfolders} disabled={config.copy_files} />
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
  main { font-family: system-ui; max-width: 750px; margin: 0 auto; padding: 20px; color: #333; }
  section { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ddd; }
  .row { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
  
  /* Tabs / Header Styling */
  .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
  .section-header h3 { margin: 0; }
  .tabs { display: flex; gap: 5px; background: #e0e0e0; padding: 4px; border-radius: 6px; }
  .tab { border: none; background: transparent; padding: 6px 16px; border-radius: 4px; cursor: pointer; font-weight: 500; color: #555; transition: 0.2s; }
  .tab:hover { color: #111; }
  .tab.active { background: #fff; color: #0066cc; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }

  /* Strategy Grid Styling */
  .strategy-grid { display: flex; gap: 20px; }
  .strategy-column { flex: 1; display: flex; flex-direction: column; gap: 10px; }
  
  /* Clickable Box Styling */
  .box-label { 
    display: block; 
    padding: 12px 15px; 
    border: 2px solid #ddd; 
    border-radius: 6px; 
    cursor: pointer; 
    background: #fff;
    transition: all 0.2s ease-in-out;
    margin: 0;
  }
  .box-label:hover { border-color: #aaa; background: #fafafa; }
  .box-label.selected { 
    border-color: #0066cc; 
    background: #e6f2ff; 
    font-weight: 600;
    color: #004499;
  }
  .box-label input[type="radio"] { display: none; }

  .nth-input-container { margin-top: 15px; display: flex; align-items: center; gap: 10px; background: #fff; padding: 10px 15px; border: 1px dashed #ccc; border-radius: 6px;}
  .inline-label { margin: 0; }
  .checkbox-label { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; cursor: pointer; }
  .checkbox-label.disabled { opacity: 0.5; cursor: not-allowed; }

  .folder-btn { padding: 8px 16px; border-radius: 4px; border: 1px solid #ccc; background: #fff; cursor: pointer; transition: 0.2s; }
  .folder-btn:hover { background: #eef; }
  button.primary { background: #0066cc; color: white; border: none; font-size: 16px; width: 100%; padding: 12px; border-radius: 6px; cursor: pointer; }
  button.primary:hover:not(:disabled) { background: #005bb5; }
  button.primary:disabled { background: #999; cursor: not-allowed; }
  .progress-container { margin-top: 20px; padding: 15px; background: #e0f7fa; border-radius: 8px; text-align: center; font-size: 1.1em;}
</style>
