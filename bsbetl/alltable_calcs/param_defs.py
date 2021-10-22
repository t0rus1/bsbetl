''' parameter definitions, consumed by params.py for alltable_calcs '''

from collections import namedtuple

# Slow Daily Average Price, SDAP:
SDAP_tuple = namedtuple('SDAP_tuple',
                        [
                            'Y1DAPu', 'e1DAPu',  # 1 up
                            'Y1DAPd', 'e1DAPd',  # 1 down
                            'Y2DAPu', 'e2DAPu',
                            'Y2DAPd', 'e2DAPd',
                            'Y3DAPu', 'e3DAPu',
                            'Y3DAPd', 'e3DAPd',
                            'Y4DAPu', 'e4DAPu',
                            'Y4DAPd', 'e4DAPd',
                            'Y5DAPu', 'e5DAPu',
                            'Y5DAPd', 'e5DAPd',
                        ]
                        )
