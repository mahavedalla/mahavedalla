function toggleOriginal(element) {
  const original = element.nextElementSibling;
  if (original.style.display === "none") {
    original.style.display = "inline";
    element.innerText = "[Hide Original]";
  } else {
    original.style.display = "none";
    element.innerText = "[Show Original]";
  }
}