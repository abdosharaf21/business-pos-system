export function buildCategoryTree(categories) {
  const byId = {};
  categories.forEach((c) => {
    byId[c.id] = { ...c, children: [] };
  });
  const roots = [];
  categories.forEach((c) => {
    const node = byId[c.id];
    const parentId = c.parent_id;
    if (parentId && byId[parentId]) {
      byId[parentId].children.push(node);
    } else {
      roots.push(node);
    }
  });
  const sortNodes = (nodes) => {
    nodes.forEach((n) => sortNodes(n.children));
    nodes.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
  };
  sortNodes(roots);
  return roots;
}

export function flattenCategoryTree(nodes, depth = 0, acc = []) {
  nodes.forEach((n) => {
    acc.push({ ...n, depth });
    flattenCategoryTree(n.children || [], depth + 1, acc);
  });
  return acc;
}
