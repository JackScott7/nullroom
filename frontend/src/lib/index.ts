export const nameColors = [
    "#FF5733",
    "#FFC300",
    "#DAF7A6",
    "#FF33F6",
    "#33FF57",
    "#33FFF6",
    "#FF3333",
    "#8E44AD",
    "#3498DB",
    "#1ABC9C",
    "#E74C3C",
    "#2ECC71",
    "#F39C12",
    "#9B59B6",
    "#34495E",
    "#F1C40F",
    "#E67E22",
    "#16A085",
    "#C0392B",
    "#27AE60",
    "#2980B9",
    "#D35400",
    "#C44569",
];

export function setRandomNameColor() {
    const color = nameColors[Math.floor(Math.random() * nameColors.length)];
    localStorage.setItem("nr_color", color);
    return color;
}