# coding = utf-8

import itertools
from copy import deepcopy

import numpy as np
import matplotlib.colors as mcolor
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase

_COLOR_SPACING = 1e-4

def normalize(arr):
    arr = np.array(arr)
    spread = max(arr) - min(arr)
    return (arr - min(arr)) / spread

def concat_index(idx1, idx2):
    len_1 = len(idx1)
    len_2 = len(idx2)
    norm_1 = normalize(idx1) * len_1
    norm_2 = normalize(idx2) * len_2
    merge = norm_1.tolist() + (norm_2 + len_1).tolist()
    return normalize(merge)

def merge_tup(pos, color):
    return [(i, *j) for i, j in zip(pos, color)]

class Segment(dict):
    r'''
    A subclass of dict which fasilitates the creation of color dict.
    '''
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

    @classmethod
    def from_value_color(cls, r_value, g_value, b_value, r_data, g_data, b_data):
        return cls.from_list(merge_tup(r_value, r_data),
                             merge_tup(g_value, g_data),
                             merge_tup(b_value, b_data))

class Colormap(mcolor.LinearSegmentedColormap):
    def __init__(self, name=None, segmentdata=None, N=256, gamma=1.0, cmap=None):
        if cmap:
            self._init_from_cmap(cmap)
        else:
            self._name = name
            self._seg = Segment(segmentdata)
            self._N = N
            self._gamma = gamma
        super().__init__(self._name, self._seg, self._N, self._gamma)

    def _init_from_cmap(self, cmap):
        if isinstance(cmap, mcolor.LinearSegmentedColormap):
            # Initialize from existing colormap
            self._name = cmap.name
            self._seg = Segment(cmap._segmentdata)
            self._N = cmap.N
            self._gamma = cmap._gamma
        if isinstance(cmap, mcolor.ListedColormap):
            carr = mcolor.to_rgba_array(cmap.colors)
            arr = np.repeat(carr, 2, axis=0)
            # Default range is 1
            idx = np.repeat(np.linspace(0, 1, cmap.N), 2)
            offset = np.array(list(itertools.islice(itertools.cycle([_COLOR_SPACING, 0]),
                                cmap.N * 2)))
            true_index = normalize((idx - offset)[1:])
            r_tup = [(i[0], i[0]) for i in arr][1:]
            g_tup = [(i[1], i[1]) for i in arr][1:]
            b_tup = [(i[2], i[2]) for i in arr][1:]
            self._name = cmap.name
            self._seg = Segment.from_value_color(true_index, true_index, true_index,
                                                 r_tup, g_tup, b_tup)
            self._N = cmap.N
            self._gamma = 1

    def __getitem__(self, n):
        if len(set([len(i) for i in self._seg.values()])) != 1:
            raise IndexError('Number of colors for each channel should be the same')
        if isinstance(n, slice):
            r = merge_tup(normalize(self._seg.red_value[n]), self._seg.red_colors[n])
            g = merge_tup(normalize(self._seg.green_value[n]), self._seg.green_colors[n])
            b = merge_tup(normalize(self._seg.blue_value[n]), self._seg.blue_colors[n])
            new_seg = Segment.from_list(r, g, b)
            return Colormap(self._name + '_seg', new_seg)

    @staticmethod
    def _merge_cmap(cmap_1, cmap_2):
        new_rv = concat_index(cmap_1._seg.red_value, cmap_2._seg.red_value)
        new_gv = concat_index(cmap_1._seg.green_value, cmap_2._seg.green_value)
        new_bv = concat_index(cmap_1._seg.blue_value, cmap_2._seg.blue_value)
        new_rcol = cmap_1._seg.red_colors + cmap_2._seg.red_colors
        new_gcol = cmap_1._seg.green_colors + cmap_2._seg.green_colors
        new_bcol = cmap_1._seg.blue_colors + cmap_2._seg.blue_colors
        seg = Segment.from_value_color(new_rv, new_gv, new_bv, new_rcol, new_gcol, new_bcol)
        return Colormap(cmap_1._name + cmap_2._name, seg)

    def __add__(self, one):
        if isinstance(one, mcolor.Colormap):
            one = Colormap(cmap=one)
        if not isinstance(one, type(self)):
            raise NotImplementedError()
        new_cmap = self._merge_cmap(self, one)
        return new_cmap

    def __radd__(self, one):
        if isinstance(one, mcolor.Colormap):
            one = Colormap(cmap=one)
        if not isinstance(one, type(self)):
            raise NotImplementedError()
        new_cmap = self._merge_cmap(one, self)
        return new_cmap  

    def set_value(self, value):
        value = normalize(value)
        new_seg = deepcopy([self._seg._red, self._seg._green, self._seg._blue])
        for color_seg in new_seg:
            for index, seg in enumerate(color_seg):
                color_seg[index] = (value[index],) + seg[1:]
        seg = Segment.from_list(*new_seg)
        return Colormap(self._name, seg, self._N, self._gamma)

    def set_color(self, color):
        pass

    def show(self):
        plt.figure(1, figsize=(11, 2))
        ax = plt.gca()
        ColorbarBase(ax, cmap=self, orientation='horizontal')
        plt.show()

    def as_mpl_cmap(self):
        return mcolor.LinearSegmentedColormap(self._name, self._seg, self._N, self._gamma)
    
    def set_uniform(self):
        return self.set_value(np.linspace(0, 1, len(self._seg._red)))