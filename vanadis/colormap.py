# coding = utf-8

import numpy as np
import matplotlib.colors as mcolor
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase

def normalize(arr):
    arr = np.array(arr)
    spread = max(arr) - min(arr)
    return (arr - min(arr)) / spread

def concat_index(idx1, idx2):
    len_1 = len(idx1)
    len_2 = len(idx2)
    len_total = len_1 + len_2
    norm_1 = normalize(idx1) * len_1
    norm_2 = normalize(idx2) * len_2
    merge = norm_1.tolist() + (norm_2 + len_1).tolist()
    return normalize(merge)

def merge_tup(pos, color):
    return [(i, *j) for i, j in zip(pos, color)]

class Segment(dict):
    def __init__(self, data):
        self._red = data['red']
        self._green = data['green']
        self._blue = data['blue']
        super().__init__(data)
    
    @property
    def red_value(self):
        return [seg[0] for seg in self._red]

    @property
    def green_value(self):
        return [seg[0] for seg in self._green]

    @property
    def blue_value(self):
        return [seg[0] for seg in self._blue]

    @property
    def red_colors(self):
        return [seg[1:] for seg in self._red]

    @property
    def green_colors(self):
        return [seg[1:] for seg in self._green]

    @property
    def blue_colors(self):
        return [seg[1:] for seg in self._blue]

    @classmethod
    def from_list(cls, red_data, green_data, blue_data):
        cdict = {'red':red_data, 'green':green_data, 'blue':blue_data}
        return cls(cdict)

class Colormap(mcolor.LinearSegmentedColormap):
    def __init__(self, name=None, segmentdata=None, N=256, gamma=1.0, cmap=None):
        if cmap:
            if isinstance(cmap, mcolor.LinearSegmentedColormap):
                # Initialize from existing colormap
                self._name = cmap.name
                self._seg = Segment(cmap._segmentdata)
                self._N = cmap.N
                self._gamma = cmap._gamma
        else:
            self._name = name
            # Need to parse segment data
            self._seg = Segment(segmentdata)
            self._N = N
            self._gamma = gamma
        super().__init__(self._name, self._seg, self._N, self._gamma)

    def __getitem__(self, n):
        if len(set([len(i) for i in self._seg.values()])) != 1:
            raise IndexError('Number of colors for each channel is not the same')
        if isinstance(n, slice):
            r = merge_tup(normalize(self._seg.red_value[n]), self._seg.red_colors[n])
            g = merge_tup(normalize(self._seg.green_value[n]), self._seg.green_colors[n])
            b = merge_tup(normalize(self._seg.blue_value[n]), self._seg.blue_colors[n])
            new_seg = Segment.from_list(r, g, b)
            return Colormap(self._name + '_seg', new_seg)

    def __add__(self, one):
        if isinstance(one, mcolor.LinearSegmentedColormap):
            one = Colormap(cmap=one)
        if not isinstance(one, type(self)):
            raise NotImplementedError()
        new_rv = concat_index(self._seg.red_value, one._seg.red_value)
        new_gv = concat_index(self._seg.green_value, one._seg.green_value)
        new_bv = concat_index(self._seg.blue_value, one._seg.blue_value)
        new_rcol = self._seg.red_colors + one._seg.red_colors
        new_gcol = self._seg.green_colors + one._seg.green_colors
        new_bcol = self._seg.blue_colors + one._seg.blue_colors
        seg = Segment.from_list(merge_tup(new_rv, new_rcol),
                                merge_tup(new_gv, new_gcol),
                                merge_tup(new_bv, new_bcol))
        return Colormap(self._name + one._name, seg)

    def set_value(self, value):
        pass

    def set_color(self, color):
        pass

def show_cmap(cmap):
    plt.figure(1, figsize=(11, 2))
    ax = plt.gca()
    ColorbarBase(ax, cmap=cmap, orientation='horizontal')
    plt.show()

if __name__ == '__main__':
    cdict = {'red':[(0.0, 0.0, 0.0),
                    (0.5, 1.0, 1.0),
                    (1.0, 1.0, 1.0)],
            'green':[(0.0, 0.0, 0.0),
                     (0.5, 1.0, 1.0),
                     (1.0, 1.0, 1.0)],
            'blue':[(0.0, 0.0, 0.0),
                    (0.5, 0.0, 0.0),
                    (1.0, 1.0, 1.0)]}
    cmap = Colormap('a', cdict)
    hsv = plt.get_cmap('hsv')
    show_cmap(cmap + hsv)