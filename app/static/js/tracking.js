async function toggleTrack(type, id, btnElement = null) {
  try {
    const response = await fetch('/api/favorite', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type: type, id: id })
    });
    const data = await response.json();
    
    if (data.success) {
      if (btnElement) {
        if (data.action === "added") {
          btnElement.classList.add("active");
          btnElement.innerText = "TRACKING ON";
        } else {
          btnElement.classList.remove("active");
          btnElement.innerText = "TRACK";
        }
      } else {
        // Called from dashboard table, where hitting "UNTRACK" removes the row visually
        const row = document.getElementById(`row-${id}`);
        if(row) row.remove();
      }
    }
  } catch(e) {
    console.error("Error toggling track", e);
  }
}
