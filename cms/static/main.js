function copyLink(link, id) {
  navigator.clipboard.writeText(link);
  document.getElementById(id).style.backgroundColor = "#0000FF";
}

