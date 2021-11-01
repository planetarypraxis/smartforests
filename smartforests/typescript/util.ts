export function findAncestor(element, selector) {
  while (
    (element = element.parentElement) &&
    !(element.matches || element.matchesSelector).call(element, selector)
  );

  return element;
}
