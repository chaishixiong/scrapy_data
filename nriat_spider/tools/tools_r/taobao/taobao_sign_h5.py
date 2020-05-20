import js2py

def get_taobaosign(time,appKey,data,token="undefined"):
    get_sign = js2py.eval_js('''function af(aR) {
                    function aC(b, a) {
                        return b << a | b >>> 32 - a
                    }
                    function aI(f, b) {
                        var h, g, d, a, c;
                        return d = 2147483648 & f,
                        a = 2147483648 & b,
                        h = 1073741824 & f,
                        g = 1073741824 & b,
                        c = (1073741823 & f) + (1073741823 & b),
                        h & g ? 2147483648 ^ c ^ d ^ a : h | g ? 1073741824 & c ? 3221225472 ^ c ^ d ^ a : 1073741824 ^ c ^ d ^ a : c ^ d ^ a
                    }
                    function aH(b, a, c) {
                        return b & a | ~b & c
                    }
                    function aE(b, a, c) {
                        return b & c | a & ~c
                    }
                    function aN(b, a, c) {
                        return b ^ a ^ c
                    }
                    function aD(b, a, c) {
                        return a ^ (b | ~c)
                    }
                    function aV(l, h, f, g, b, d, m) {
                        return l = aI(l, aI(aI(aH(h, f, g), b), m)),
                        aI(aC(l, d), h)
                    }
                    function aB(h, l, f, g, b, d, m) {
                        return h = aI(h, aI(aI(aE(l, f, g), b), m)),
                        aI(aC(h, d), l)
                    }
                    function aT(h, i, g, f, b, d, l) {
                        return h = aI(h, aI(aI(aN(i, g, f), b), l)),
                        aI(aC(h, d), i)
                    }
                    function aG(h, l, g, f, b, d, m) {
                        return h = aI(h, aI(aI(aD(l, g, f), b), m)),
                        aI(aC(h, d), l)
                    }
                    function aQ(g) {
                        for (var m, d = g.length, c = d + 8, b = (c - c % 64) / 64, f = 16 * (b + 1), p = new Array(f - 1), h = 0, l = 0; d > l; ) {
                            m = (l - l % 4) / 4,
                            h = l % 4 * 8,
                            p[m] = p[m] | g.charCodeAt(l) << h,
                            l++
                        }
                        return m = (l - l % 4) / 4,
                        h = l % 4 * 8,
                        p[m] = p[m] | 128 << h,
                        p[f - 2] = d << 3,
                        p[f - 1] = d >>> 29,
                        p
                    }
                    function aK(c) {
                        var a, f, d = "", b = "";
                        for (f = 0; 3 >= f; f++) {
                            a = c >>> 8 * f & 255,
                            b = "0" + a.toString(16),
                            d += b.substr(b.length - 2, 2)
                        }
                        return d
                    }
                    function aS(b) {
                        b = b.replace(/\\r\\n/g, "\\n");
                        for (var a = "", d = 0; d < b.length; d++) {
                            var c = b.charCodeAt(d);
                            128 > c ? a += String.fromCharCode(c) : c > 127 && 2048 > c ? (a += String.fromCharCode(c >> 6 | 192),
                            a += String.fromCharCode(63 & c | 128)) : (a += String.fromCharCode(c >> 12 | 224),
                            a += String.fromCharCode(c >> 6 & 63 | 128),
                            a += String.fromCharCode(63 & c | 128))
                        }
                        return a
                    }
                    var aJ, aO, aA, aP, az, ax, aW, at, aj, aU = [], ah = 7, al = 12, ai = 17, ay = 22, av = 5, aw = 9, aF = 14, am = 20, aL = 4, ak = 11, au = 16, ao = 23, aq = 6, aM = 10, ap = 15, ar = 21;
                    for (aR = aS(aR),
                    aU = aQ(aR),
                    ax = 1732584193,
                    aW = 4023233417,
                    at = 2562383102,
                    aj = 271733878,
                    aJ = 0; aJ < aU.length; aJ += 16) {
                        aO = ax,
                        aA = aW,
                        aP = at,
                        az = aj,
                        ax = aV(ax, aW, at, aj, aU[aJ + 0], ah, 3614090360),
                        aj = aV(aj, ax, aW, at, aU[aJ + 1], al, 3905402710),
                        at = aV(at, aj, ax, aW, aU[aJ + 2], ai, 606105819),
                        aW = aV(aW, at, aj, ax, aU[aJ + 3], ay, 3250441966),
                        ax = aV(ax, aW, at, aj, aU[aJ + 4], ah, 4118548399),
                        aj = aV(aj, ax, aW, at, aU[aJ + 5], al, 1200080426),
                        at = aV(at, aj, ax, aW, aU[aJ + 6], ai, 2821735955),
                        aW = aV(aW, at, aj, ax, aU[aJ + 7], ay, 4249261313),
                        ax = aV(ax, aW, at, aj, aU[aJ + 8], ah, 1770035416),
                        aj = aV(aj, ax, aW, at, aU[aJ + 9], al, 2336552879),
                        at = aV(at, aj, ax, aW, aU[aJ + 10], ai, 4294925233),
                        aW = aV(aW, at, aj, ax, aU[aJ + 11], ay, 2304563134),
                        ax = aV(ax, aW, at, aj, aU[aJ + 12], ah, 1804603682),
                        aj = aV(aj, ax, aW, at, aU[aJ + 13], al, 4254626195),
                        at = aV(at, aj, ax, aW, aU[aJ + 14], ai, 2792965006),
                        aW = aV(aW, at, aj, ax, aU[aJ + 15], ay, 1236535329),
                        ax = aB(ax, aW, at, aj, aU[aJ + 1], av, 4129170786),
                        aj = aB(aj, ax, aW, at, aU[aJ + 6], aw, 3225465664),
                        at = aB(at, aj, ax, aW, aU[aJ + 11], aF, 643717713),
                        aW = aB(aW, at, aj, ax, aU[aJ + 0], am, 3921069994),
                        ax = aB(ax, aW, at, aj, aU[aJ + 5], av, 3593408605),
                        aj = aB(aj, ax, aW, at, aU[aJ + 10], aw, 38016083),
                        at = aB(at, aj, ax, aW, aU[aJ + 15], aF, 3634488961),
                        aW = aB(aW, at, aj, ax, aU[aJ + 4], am, 3889429448),
                        ax = aB(ax, aW, at, aj, aU[aJ + 9], av, 568446438),
                        aj = aB(aj, ax, aW, at, aU[aJ + 14], aw, 3275163606),
                        at = aB(at, aj, ax, aW, aU[aJ + 3], aF, 4107603335),
                        aW = aB(aW, at, aj, ax, aU[aJ + 8], am, 1163531501),
                        ax = aB(ax, aW, at, aj, aU[aJ + 13], av, 2850285829),
                        aj = aB(aj, ax, aW, at, aU[aJ + 2], aw, 4243563512),
                        at = aB(at, aj, ax, aW, aU[aJ + 7], aF, 1735328473),
                        aW = aB(aW, at, aj, ax, aU[aJ + 12], am, 2368359562),
                        ax = aT(ax, aW, at, aj, aU[aJ + 5], aL, 4294588738),
                        aj = aT(aj, ax, aW, at, aU[aJ + 8], ak, 2272392833),
                        at = aT(at, aj, ax, aW, aU[aJ + 11], au, 1839030562),
                        aW = aT(aW, at, aj, ax, aU[aJ + 14], ao, 4259657740),
                        ax = aT(ax, aW, at, aj, aU[aJ + 1], aL, 2763975236),
                        aj = aT(aj, ax, aW, at, aU[aJ + 4], ak, 1272893353),
                        at = aT(at, aj, ax, aW, aU[aJ + 7], au, 4139469664),
                        aW = aT(aW, at, aj, ax, aU[aJ + 10], ao, 3200236656),
                        ax = aT(ax, aW, at, aj, aU[aJ + 13], aL, 681279174),
                        aj = aT(aj, ax, aW, at, aU[aJ + 0], ak, 3936430074),
                        at = aT(at, aj, ax, aW, aU[aJ + 3], au, 3572445317),
                        aW = aT(aW, at, aj, ax, aU[aJ + 6], ao, 76029189),
                        ax = aT(ax, aW, at, aj, aU[aJ + 9], aL, 3654602809),
                        aj = aT(aj, ax, aW, at, aU[aJ + 12], ak, 3873151461),
                        at = aT(at, aj, ax, aW, aU[aJ + 15], au, 530742520),
                        aW = aT(aW, at, aj, ax, aU[aJ + 2], ao, 3299628645),
                        ax = aG(ax, aW, at, aj, aU[aJ + 0], aq, 4096336452),
                        aj = aG(aj, ax, aW, at, aU[aJ + 7], aM, 1126891415),
                        at = aG(at, aj, ax, aW, aU[aJ + 14], ap, 2878612391),
                        aW = aG(aW, at, aj, ax, aU[aJ + 5], ar, 4237533241),
                        ax = aG(ax, aW, at, aj, aU[aJ + 12], aq, 1700485571),
                        aj = aG(aj, ax, aW, at, aU[aJ + 3], aM, 2399980690),
                        at = aG(at, aj, ax, aW, aU[aJ + 10], ap, 4293915773),
                        aW = aG(aW, at, aj, ax, aU[aJ + 1], ar, 2240044497),
                        ax = aG(ax, aW, at, aj, aU[aJ + 8], aq, 1873313359),
                        aj = aG(aj, ax, aW, at, aU[aJ + 15], aM, 4264355552),
                        at = aG(at, aj, ax, aW, aU[aJ + 6], ap, 2734768916),
                        aW = aG(aW, at, aj, ax, aU[aJ + 13], ar, 1309151649),
                        ax = aG(ax, aW, at, aj, aU[aJ + 4], aq, 4149444226),
                        aj = aG(aj, ax, aW, at, aU[aJ + 11], aM, 3174756917),
                        at = aG(at, aj, ax, aW, aU[aJ + 2], ap, 718787259),
                        aW = aG(aW, at, aj, ax, aU[aJ + 9], ar, 3951481745),
                        ax = aI(ax, aO),
                        aW = aI(aW, aA),
                        at = aI(at, aP),
                        aj = aI(aj, az)
                    }
                    var an = aK(ax) + aK(aW) + aK(at) + aK(aj);
                    return an.toLowerCase()
                }''')
    sign_str = "{}&{}&{}&{}".format(token, time, appKey, data)
    a = get_sign(sign_str)
    return a

if __name__=="__main__":
    import time
    time_now = str(time.time())
    appkey = "12574478"
    data = '{}'
    sign = get_taobaosign(time=time_now,appKey=appkey,data=data)
    print(sign)
