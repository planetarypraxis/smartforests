export function findAncestor(element, selector) {
  while (
    (element = element.parentElement) &&
    !(element.matches || element.matchesSelector).call(element, selector)
  );

  return element;
}

const ONE_HOUR_IN_SECONDS = 60 * 60

export function formatDuration(seconds: number): string {
  var date = new Date()
  date.setUTCHours(0, 0, 0, 0)
  date.setSeconds(seconds);
  var timeString = date.toTimeString().split(" ")[0]
  if (seconds < ONE_HOUR_IN_SECONDS) {
    // Hide the hours
    timeString = timeString.replace(/^00:/gim, '')
  }
  return timeString
}