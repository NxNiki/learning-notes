
// Sets:
let bands = new Set();
bands.add("Journey");
bands.add("Reo Speedwagon");
bands.add("styx");

if (bands.has("Journey")) {
  console.log("Journey is in the bands");
}

for (const band of bands) {
  console.log(band);
}

// Maps:
let team = new Map(
  [
    ["pitcher", "Ron Guidry"],
    ["catcher", "Rick Cerone"],
    ["centerfield", "Dave Winfield"]
  ]
);
team.set("thirdbase", "Graig Nettles");
console.log(team.get("pitcher"));

for (const [key, value] of team) {
  console.log(key, value);
}
