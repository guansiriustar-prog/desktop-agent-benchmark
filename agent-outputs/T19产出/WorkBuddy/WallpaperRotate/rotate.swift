import AppKit
import Foundation

let folder = URL(fileURLWithPath: "/Users/<user>/Desktop/横评/测试图片", isDirectory: true)
let supportDir = FileManager.default.homeDirectoryForCurrentUser
    .appendingPathComponent("Library/Application Support/WallpaperRotate", isDirectory: true)
let stateURL = supportDir.appendingPathComponent("index.txt")
let fm = FileManager.default

let extensions = ["png", "jpg", "jpeg", "heic", "tiff", "bmp", "gif"]
let images = (try? fm.contentsOfDirectory(at: folder, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles]))?
    .filter { extensions.contains($0.pathExtension.lowercased()) }
    .sorted { $0.lastPathComponent < $1.lastPathComponent } ?? []

guard !images.isEmpty else {
    FileHandle.standardError.write("No images found in \(folder.path)\n".data(using: .utf8)!)
    exit(1)
}

var index = 0
if let text = try? String(contentsOf: stateURL, encoding: .utf8),
   let saved = Int(text.trimmingCharacters(in: .whitespacesAndNewlines)) {
    index = saved
}
index = ((index % images.count) + images.count) % images.count

let url = images[index]
let screens = NSScreen.screens
if screens.isEmpty {
    FileHandle.standardError.write("No active screens\n".data(using: .utf8)!)
    exit(1)
}
for screen in screens {
    try? NSWorkspace.shared.setDesktopImageURL(url, for: screen, options: [:])
}
print("wallpaper -> \(url.lastPathComponent)")

let next = (index + 1) % images.count
try? String(next).write(to: stateURL, atomically: true, encoding: .utf8)
