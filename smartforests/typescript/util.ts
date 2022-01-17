export function findAncestor(element, selector) {
  while (
    (element = element.parentElement) &&
    !(element.matches || element.matchesSelector).call(element, selector)
  );

  return element;
}

export function formatDuration(seconds: number): string {
  console.log(seconds)
  var date = new Date()
  date.setUTCHours(0, 0, 0, 0)
  date.setSeconds(seconds);
  var timeString = date.toTimeString().split(" ")[0]
  return timeString
}