// system-map.local.example.js  →  copy to system-map.local.js (gitignored) and
// fill in your REAL hardware specs. The committed map/PNG show only placeholders;
// real specs never enter git. system-map.html loads this via a plain <script>
// (works under file://, no CORS) and merges it over the placeholder DATA.compute.
//
//   cp system-map.local.example.js system-map.local.js   # then edit, then render
//
// You can override any DATA key here, not just compute — same shape as DATA.
window.LOCAL = {
  compute: {
    gpu: "GPU · &lt;your GPU model&gt; · &lt;NN&gt; GB",
    cpu: "CPU · &lt;your CPU model&gt; · &lt;n&gt;c/&lt;n&gt;t",
    ram: "RAM · &lt;NN&gt; GB"
  }
};
