export function getBezierPath(start, end) {
  const dx = end[0] - start[0];
  const dy = end[1] - start[1];
  const cp = [start[0] + dx * 0.25, start[1] + dy * 0.75];
  return cp;
}

export function getQuadraticBezierXY(t, start, cp, end) {
  const x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * cp[0] + t**2 * end[0];
  const y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * cp[1] + t**2 * end[1];
  return [x, y];
}