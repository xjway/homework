from PIL import Image
import matplotlib.pyplot as plt
import math
import copy
class BilateralFilter(object):
    def __init__(self, ds, rs, radiu):
        """初始化变量"""
        self.ds = ds
        self.rs = rs
        self.c_weight_table = []
        self.s_weight_table = []
        self.radius = radiu

    def build_distance_weight_table(self):
        """定义空间域模板"""
        #        size = 2 * self.radius + 1
        for semi_row in range(-self.radius, self.radius + 1):
            self.c_weight_table.append([])
            for semi_col in range(-self.radius, self.radius + 1):
                # calculate Euclidean distance between center point and close pixels
                delta = -(semi_row * semi_row + semi_col * semi_col) / (2 * (self.ds ** 2))
                self.c_weight_table[semi_row + self.radius].append(
                    math.exp(delta))

    def build_similarity_weight_table(self):
        """定义值域模板"""
        for i in range(256):  # since the color scope is 0 ~ 255
            delta = -(i * i) / (2 * (self.rs ** 2))
            self.s_weight_table.append(math.exp(delta))

    def clamp(self, p):
        if p < 0:
            return 0
        elif p > 255:
            return 255
        else:
            return p

    def bilateral_filter(self, src):
        """
        双边滤波器的方法：对原始图进行双边滤波器平滑，并返回平滑过后的图
        """
        height = src.size[0]
        width = src.size[1]
        radius = self.radius
        self.build_distance_weight_table()
        self.build_similarity_weight_table()
        in_pixels = src.load()
        raw_data = []
        out_data = copy.deepcopy(src)
        #        out_pixels = {}
        red_sum = green_sum = blue_sum = 0  # result of convolution before normalization
        cs_sum_red_weight = cs_sum_green_weight = cs_sum_blue_weight = 0  # normalization
        # 对于边缘像素采用不平滑的方法
        for row in range(radius, height - radius):
            for col in range(radius, width - radius):
                # 对每个像素进行平滑
                tr = in_pixels[row, col][0]
                tg = in_pixels[row, col][1]
                tb = in_pixels[row, col][2]
                raw_data.append((tr, tg, tb))
                for semi_row in range(-radius, radius + 1):
                    for semi_col in range(-radius, radius + 1):
                        # 获得模板内的像素
                        row_offset = row + semi_row
                        col_offset = col + semi_col
                        tr2 = in_pixels[row_offset, col_offset][0]
                        tg2 = in_pixels[row_offset, col_offset][1]
                        tb2 = in_pixels[row_offset, col_offset][2]
                        # 卷积计算
                        cs_red_weight = (
                                self.c_weight_table[semi_row + radius][semi_col + radius]
                                * self.s_weight_table[(abs(tr2 - tr))]
                        )
                        cs_green_weight = (
                                self.c_weight_table[semi_row + radius][semi_col + radius]
                                * self.s_weight_table[(abs(tg2 - tg))]
                        )
                        cs_blue_weight = (
                                self.c_weight_table[semi_row + radius][semi_col + radius]
                                * self.s_weight_table[(abs(tb2 - tb))]
                        )

                        cs_sum_red_weight += cs_red_weight
                        cs_sum_blue_weight += cs_blue_weight
                        cs_sum_green_weight += cs_green_weight

                        red_sum += cs_red_weight * float(tr2)
                        green_sum += cs_green_weight * float(tg2)
                        blue_sum += cs_blue_weight * float(tb2)
                # 归一化过程
                tr = int(math.floor(red_sum / cs_sum_red_weight))
                tg = int(math.floor(green_sum / cs_sum_green_weight))
                tb = int(math.floor(blue_sum / cs_sum_blue_weight))
                temp_rgb = (self.clamp(tr), self.clamp(tg), self.clamp(tb))
                out_data.putpixel((row, col), temp_rgb)
                # clean value for next time
                red_sum = green_sum = blue_sum = 0
                cs_red_weight = cs_green_weight = cs_blue_weight = 0
                cs_sum_red_weight = cs_sum_blue_weight = cs_sum_green_weight = 0
        return out_data


def main():
    img0 = Image.open('lena_10.jpg')
    bf = BilateralFilter(10, 30, 1)
    dest0 = bf.bilateral_filter(img0)
    dest0.save('out_1.jpg')

    bf = BilateralFilter(10, 30, 5)
    dest1 = bf.bilateral_filter(img0)
    dest1.save('out_2.jpg')

    bf = BilateralFilter(100, 100, 10)
    dest1 = bf.bilateral_filter(img0)
    dest1.save('out_3.jpg')

    plt.figure(figsize=(18, 12))
    plt.subplot(2, 2, 1)
    plt.title("Origin", fontsize=20)
    plt.imshow(img0)
    plt.axis('off')

    plt.subplot(2, 2, 2)
    plt.title("ds=10,rs=30,radius=1", fontsize=20)
    plt.imshow(dest0)
    plt.axis('off')

    plt.subplot(2, 2, 3)
    plt.title("ds=10,rs=30,radius=5", fontsize=20)
    plt.imshow(dest1)
    plt.axis('off')

    plt.subplot(2, 2, 4)
    plt.title("ds=100,rs=100,radius=10", fontsize=20)
    plt.imshow(dest1)
    plt.axis('off')

    plt.show()


if __name__ == '__main__':
    main()
