export const nav = ["Dashboard", "Rooms", "Devices", "Scenes", "Automations", "AI Assistant", "CCTV & Security", "Energy", "Water", "Climate", "Access Control", "Notifications", "Timeline", "Reports", "Settings"];
export const rooms = [
  ["Living Room", "24", "2.1", 6, "blue", "living"], ["Master Bedroom", "23", "1.5", 5, "purple", "master"], ["Kitchen", "26", "2.4", 7, "orange", "kitchen"], ["Garden", "28", "0.8", 4, "green", "garden"],
  ["Home Theatre", "23", "1.8", 4, "red", "living"], ["Bedroom 2", "24", "1.2", 4, "cyan", "master"], ["Dining Area", "25", "1.0", 3, "gold", "kitchen"], ["Parking / Gate", "28", "0.6", 3, "blue", "garden"]
].map(([name,temp,power,devices,accent,apiRoom], scene) => ({name,temp,power,devices,accent,apiRoom,scene,on:true}));
