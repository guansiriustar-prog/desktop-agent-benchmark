import CoreGraphics
import Foundation
let opts: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
let list = CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as! [[String: Any]]
for w in list.prefix(40) {
    let owner = w[kCGWindowOwnerName as String] as? String ?? "?"
    let name = w[kCGWindowName as String] as? String ?? ""
    let layer = w[kCGWindowLayer as String] as? Int ?? -1
    let alpha = w[kCGWindowAlpha as String] as? Double ?? -1
    let b = w[kCGWindowBounds as String] as? [String: Double] ?? [:]
    let num = w[kCGWindowNumber as String] as? Int ?? -1
    print(String(format: "%6d L%-4d a%.2f  x%5.0f y%5.0f w%5.0f h%5.0f  %@ | %@", num, layer, alpha, b["X"] ?? 0, b["Y"] ?? 0, b["Width"] ?? 0, b["Height"] ?? 0, owner, name))
}
