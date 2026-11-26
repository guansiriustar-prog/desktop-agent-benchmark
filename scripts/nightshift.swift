// Read (and only with an explicit "restore" argument, write back) the Night Shift schedule via CoreBrightness.
// Usage: nightshift            -> print status
//        nightshift restore M FH FM TH TM  -> set schedule times and mode (used only to put the user's original values back)
import Foundation
let path = "/System/Library/PrivateFrameworks/CoreBrightness.framework"
guard let b = Bundle(path: path), b.load(), let cls = NSClassFromString("CBBlueLightClient") as? NSObject.Type else { print("cannot load CoreBrightness"); exit(1) }
let client = cls.init()
func status() -> (active: Bool, enabled: Bool, sunOK: Bool, mode: Int32, fh: Int32, fm: Int32, th: Int32, tm: Int32, available: Bool) {
    let buf = UnsafeMutableRawPointer.allocate(byteCount: 64, alignment: 8); buf.initializeMemory(as: UInt8.self, repeating: 0, count: 64)
    defer { buf.deallocate() }
    let sel = NSSelectorFromString("getBlueLightStatus:")
    typealias F = @convention(c) (AnyObject, Selector, UnsafeMutableRawPointer) -> Bool
    let f = unsafeBitCast(client.method(for: sel), to: F.self)
    _ = f(client, sel, buf)
    let i = { (o: Int) in buf.load(fromByteOffset: o, as: Int32.self) }
    let c = { (o: Int) in buf.load(fromByteOffset: o, as: UInt8.self) != 0 }
    return (c(0), c(1), c(2), i(4), i(8), i(12), i(16), i(20), c(32))
}
let args = CommandLine.arguments
if args.count >= 7 && args[1] == "restore" {
    let v = args[2...6].map { Int32($0)! }
    var sched: [Int32] = [v[1], v[2], v[3], v[4]]
    typealias FS = @convention(c) (AnyObject, Selector, UnsafeMutableRawPointer) -> Bool
    let ss = NSSelectorFromString("setSchedule:")
    let okS = sched.withUnsafeMutableBytes { p in unsafeBitCast(client.method(for: ss), to: FS.self)(client, ss, p.baseAddress!) }
    typealias FM = @convention(c) (AnyObject, Selector, Int32) -> Bool
    let sm = NSSelectorFromString("setMode:")
    let okM = unsafeBitCast(client.method(for: sm), to: FM.self)(client, sm, v[0])
    print("restore setSchedule=\(okS) setMode=\(okM)")
    Thread.sleep(forTimeInterval: 1)
}
let s = status()
let modeName = [0: "关闭", 1: "日落到日出", 2: "自定"][Int(s.mode)] ?? "?"
print(String(format: "%@ mode=%d(%@) from %02d:%02d to %02d:%02d enabled(now on)=%@ active=%@ sunOK=%@ available=%@", DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium), s.mode, modeName, s.fh, s.fm, s.th, s.tm, s.enabled ? "Y":"N", s.active ? "Y":"N", s.sunOK ? "Y":"N", s.available ? "Y":"N"))
