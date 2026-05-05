export const nameColors = [
    "#ff3a3a",
    "#ff5c1b",
    "#f7992d",
    "#fbff13",
    "#c4ff22",
    "#6aff5d",
    "#45ffb1",
    "#00ff2a",
    "#28ffc9",
    "#20a6ff",
    "#20ddff",
    "#178fff",
    "#5b3eff",
    "#7d45ff",
    "#c45fff",
    "#d058ff",
    "#ff08de",
    "#ff20bc",
    "#ff1395",
    "#27AE60",
    "#ff2869",
    "#616161",
    "#313131",
];

export function setRandomNameColor() {
    const color = nameColors[Math.floor(Math.random() * nameColors.length)];
    localStorage.setItem("nr_color", color);
    return color;
}