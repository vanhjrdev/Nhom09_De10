# Do nhieu tham so GA / GA_LS (thanh vien C)

- Ngân sách: 1.0 giây/lần chạy
- Seeds: 1, 2, 3
- Thuật toán: GA và GA_LS

## Thiết kế
- Quét một tham số mỗi lần, giữ tham số kia ở giá trị mặc định.
- Mặc định: population = 40, mutation_rate = 1/n.

## Kết quả tóm tắt (theo instance / tham số / thuật toán)

| Instance | Thuật toán | Tham số | Giá trị | Best | Mean ± Std | Feasible |
|---|---|---|---|---|---|---|
| scp51 | GA | mutation_rate | 0.5x1/n | 258 | 264.00 ± 4.24 | 100% |
| scp51 | GA | mutation_rate | 1.0x1/n | 258 | 264.00 ± 4.24 | 100% |
| scp51 | GA | mutation_rate | 10.0x1/n | 258 | 264.67 ± 4.71 | 100% |
| scp51 | GA | mutation_rate | 2.0x1/n | 264 | 266.00 ± 1.41 | 100% |
| scp51 | GA | mutation_rate | 5.0x1/n | 256 | 257.00 ± 0.82 | 100% |
| scp51 | GA | population | 10 | 267 | 269.33 ± 2.05 | 100% |
| scp51 | GA | population | 160 | 274 | 276.33 ± 1.70 | 100% |
| scp51 | GA | population | 20 | 264 | 266.33 ± 2.05 | 100% |
| scp51 | GA | population | 40 | 258 | 264.00 ± 4.24 | 100% |
| scp51 | GA | population | 80 | 256 | 258.67 ± 3.09 | 100% |
| scp51 | GA_LS | mutation_rate | 0.5x1/n | 254 | 261.33 ± 5.19 | 100% |
| scp51 | GA_LS | mutation_rate | 1.0x1/n | 255 | 260.67 ± 4.03 | 100% |
| scp51 | GA_LS | mutation_rate | 10.0x1/n | 253 | 260.67 ± 5.56 | 100% |
| scp51 | GA_LS | mutation_rate | 2.0x1/n | 253 | 259.00 ± 4.55 | 100% |
| scp51 | GA_LS | mutation_rate | 5.0x1/n | 254 | 256.00 ± 1.63 | 100% |
| scp51 | GA_LS | population | 10 | 266 | 268.33 ± 2.05 | 100% |
| scp51 | GA_LS | population | 160 | 268 | 270.33 ± 3.30 | 100% |
| scp51 | GA_LS | population | 20 | 256 | 261.33 ± 3.86 | 100% |
| scp51 | GA_LS | population | 40 | 255 | 260.67 ± 4.03 | 100% |
| scp51 | GA_LS | population | 80 | 253 | 254.33 ± 1.25 | 100% |
| scp61 | GA | mutation_rate | 0.5x1/n | 141 | 141.33 ± 0.47 | 100% |
| scp61 | GA | mutation_rate | 1.0x1/n | 141 | 143.00 ± 2.83 | 100% |
| scp61 | GA | mutation_rate | 10.0x1/n | 141 | 141.00 ± 0.00 | 100% |
| scp61 | GA | mutation_rate | 2.0x1/n | 141 | 141.67 ± 0.94 | 100% |
| scp61 | GA | mutation_rate | 5.0x1/n | 141 | 141.00 ± 0.00 | 100% |
| scp61 | GA | population | 10 | 144 | 148.33 ± 4.78 | 100% |
| scp61 | GA | population | 160 | 143 | 144.67 ± 1.70 | 100% |
| scp61 | GA | population | 20 | 146 | 146.67 ± 0.94 | 100% |
| scp61 | GA | population | 40 | 141 | 143.00 ± 2.83 | 100% |
| scp61 | GA | population | 80 | 141 | 141.33 ± 0.47 | 100% |
| scp61 | GA_LS | mutation_rate | 0.5x1/n | 140 | 141.67 ± 1.70 | 100% |
| scp61 | GA_LS | mutation_rate | 1.0x1/n | 141 | 141.00 ± 0.00 | 100% |
| scp61 | GA_LS | mutation_rate | 10.0x1/n | 141 | 142.00 ± 1.41 | 100% |
| scp61 | GA_LS | mutation_rate | 2.0x1/n | 142 | 142.67 ± 0.47 | 100% |
| scp61 | GA_LS | mutation_rate | 5.0x1/n | 141 | 142.00 ± 0.82 | 100% |
| scp61 | GA_LS | population | 10 | 143 | 143.33 ± 0.47 | 100% |
| scp61 | GA_LS | population | 160 | 143 | 144.00 ± 1.41 | 100% |
| scp61 | GA_LS | population | 20 | 142 | 142.33 ± 0.47 | 100% |
| scp61 | GA_LS | population | 40 | 141 | 141.00 ± 0.00 | 100% |
| scp61 | GA_LS | population | 80 | 140 | 140.67 ± 0.94 | 100% |
| vua_150x600_s202 | GA | mutation_rate | 0.5x1/n | 269 | 276.00 ± 4.97 | 100% |
| vua_150x600_s202 | GA | mutation_rate | 1.0x1/n | 270 | 276.00 ± 4.24 | 100% |
| vua_150x600_s202 | GA | mutation_rate | 10.0x1/n | 269 | 272.33 ± 2.49 | 100% |
| vua_150x600_s202 | GA | mutation_rate | 2.0x1/n | 273 | 277.00 ± 4.97 | 100% |
| vua_150x600_s202 | GA | mutation_rate | 5.0x1/n | 269 | 275.00 ± 5.35 | 100% |
| vua_150x600_s202 | GA | population | 10 | 277 | 287.33 ± 7.32 | 100% |
| vua_150x600_s202 | GA | population | 160 | 261 | 263.67 ± 3.77 | 100% |
| vua_150x600_s202 | GA | population | 20 | 278 | 280.00 ± 2.16 | 100% |
| vua_150x600_s202 | GA | population | 40 | 270 | 276.00 ± 4.24 | 100% |
| vua_150x600_s202 | GA | population | 80 | 261 | 266.00 ± 3.56 | 100% |
| vua_150x600_s202 | GA_LS | mutation_rate | 0.5x1/n | 268 | 268.67 ± 0.47 | 100% |
| vua_150x600_s202 | GA_LS | mutation_rate | 1.0x1/n | 268 | 268.67 ± 0.47 | 100% |
| vua_150x600_s202 | GA_LS | mutation_rate | 10.0x1/n | 261 | 261.00 ± 0.00 | 100% |
| vua_150x600_s202 | GA_LS | mutation_rate | 2.0x1/n | 261 | 265.67 ± 3.30 | 100% |
| vua_150x600_s202 | GA_LS | mutation_rate | 5.0x1/n | 261 | 263.67 ± 3.77 | 100% |
| vua_150x600_s202 | GA_LS | population | 10 | 268 | 270.00 ± 2.16 | 100% |
| vua_150x600_s202 | GA_LS | population | 160 | 261 | 261.00 ± 0.00 | 100% |
| vua_150x600_s202 | GA_LS | population | 20 | 261 | 267.67 ± 4.99 | 100% |
| vua_150x600_s202 | GA_LS | population | 40 | 268 | 268.67 ± 0.47 | 100% |
| vua_150x600_s202 | GA_LS | population | 80 | 261 | 264.00 ± 2.94 | 100% |
| vua_200x1000_s203 | GA | mutation_rate | 0.5x1/n | 319 | 320.00 ± 0.82 | 100% |
| vua_200x1000_s203 | GA | mutation_rate | 1.0x1/n | 319 | 320.00 ± 0.82 | 100% |
| vua_200x1000_s203 | GA | mutation_rate | 10.0x1/n | 318 | 321.00 ± 2.45 | 100% |
| vua_200x1000_s203 | GA | mutation_rate | 2.0x1/n | 319 | 319.00 ± 0.00 | 100% |
| vua_200x1000_s203 | GA | mutation_rate | 5.0x1/n | 315 | 320.00 ± 3.74 | 100% |
| vua_200x1000_s203 | GA | population | 10 | 328 | 336.33 ± 6.55 | 100% |
| vua_200x1000_s203 | GA | population | 160 | 319 | 335.00 ± 22.63 | 100% |
| vua_200x1000_s203 | GA | population | 20 | 317 | 323.67 ± 4.78 | 100% |
| vua_200x1000_s203 | GA | population | 40 | 319 | 320.00 ± 0.82 | 100% |
| vua_200x1000_s203 | GA | population | 80 | 317 | 318.00 ± 1.41 | 100% |
| vua_200x1000_s203 | GA_LS | mutation_rate | 0.5x1/n | 318 | 318.67 ± 0.47 | 100% |
| vua_200x1000_s203 | GA_LS | mutation_rate | 1.0x1/n | 317 | 318.33 ± 0.94 | 100% |
| vua_200x1000_s203 | GA_LS | mutation_rate | 10.0x1/n | 319 | 319.33 ± 0.47 | 100% |
| vua_200x1000_s203 | GA_LS | mutation_rate | 2.0x1/n | 318 | 318.67 ± 0.47 | 100% |
| vua_200x1000_s203 | GA_LS | mutation_rate | 5.0x1/n | 317 | 317.33 ± 0.47 | 100% |
| vua_200x1000_s203 | GA_LS | population | 10 | 320 | 326.00 ± 5.89 | 100% |
| vua_200x1000_s203 | GA_LS | population | 160 | 319 | 320.00 ± 0.82 | 100% |
| vua_200x1000_s203 | GA_LS | population | 20 | 319 | 321.00 ± 2.16 | 100% |
| vua_200x1000_s203 | GA_LS | population | 40 | 317 | 318.33 ± 0.94 | 100% |
| vua_200x1000_s203 | GA_LS | population | 80 | 317 | 318.33 ± 0.94 | 100% |

Tổng số lần chạy: 240
File chi tiết: ga_sensitivity.csv
