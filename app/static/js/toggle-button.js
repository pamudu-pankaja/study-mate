function toggleOff(clickedCheckbox) {
  const group = document.getElementById('resourceToggleGroup');
  const checkboxes = group.querySelectorAll('input[type="checkbox"]');

  checkboxes.forEach(cb => {
    if (cb !== clickedCheckbox) cb.checked = false;
  });
}
