export const fetchDrainData = async (blockId) => {
  const blockCenters = {
    1: [127.0286, 37.4979],
    2: [127.0366, 37.5009],
    3: [127.0232, 37.5042],
    4: [127.0277, 37.4941],
    5: [127.0412, 37.5032]
  };

  const radius = 0.0003; // 약 30m
  const center = blockCenters[blockId];
  const nodes = [];

  for (let i = 0; i < 4; i++) {
    const angle = (i * Math.PI) / 2;
    const lng = center[0] + radius * Math.cos(angle);
    const lat = center[1] + radius * Math.sin(angle);
    
    nodes.push({
      id: i + 1,
      block: blockId,
      location_x: lat,
      location_y: lng
    });
  }

  return nodes;
};
