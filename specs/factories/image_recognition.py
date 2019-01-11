""" Defines mocked Google Cloud Vision API responses """
from unittest.mock import patch

mock_image_recognition = patch('application.controllers.artifacts_controller.recognize_image', return_value=None)


def vision_api_response():
    return {
        "responses": [
            {
                "labelAnnotations": [
                    {
                        "mid": "/m/07s6nbt",
                        "description": "text",
                        "score": 0.95953727,
                        "topicality": 0.95953727
                    },
                    {
                        "mid": "/m/03gq5hm",
                        "description": "font",
                        "score": 0.8794061,
                        "topicality": 0.8794061
                    },
                    {
                        "mid": "/m/01jwgf",
                        "description": "product",
                        "score": 0.79753035,
                        "topicality": 0.79753035
                    },
                    {
                        "mid": "/m/03scnj",
                        "description": "line",
                        "score": 0.7704755,
                        "topicality": 0.7704755
                    },
                    {
                        "mid": "/m/0n0j",
                        "description": "area",
                        "score": 0.6720096,
                        "topicality": 0.6720096
                    },
                    {
                        "mid": "/m/05fwb",
                        "description": "number",
                        "score": 0.58606523,
                        "topicality": 0.58606523
                    },
                    {
                        "mid": "/m/0mwc",
                        "description": "angle",
                        "score": 0.54746825,
                        "topicality": 0.54746825
                    },
                    {
                        "mid": "/m/015bv3",
                        "description": "document",
                        "score": 0.54727286,
                        "topicality": 0.54727286
                    },
                    {
                        "mid": "/m/086nh",
                        "description": "web page",
                        "score": 0.546925,
                        "topicality": 0.546925
                    },
                    {
                        "mid": "/m/03qh03g",
                        "description": "media",
                        "score": 0.5365899,
                        "topicality": 0.5365899
                    }
                ],
                "textAnnotations": [
                    {
                        "locale": "en",
                        "description": "Regular Meeting Django-Project\nby Arne Zerndt 7 days ago Print\nO\nAll times displayed in Europe/Berlin\nTick the checkboxes twice to select \"Yes, if need be\" vote\nTable Calendar\nNov\nNov\nNov\nNov\nNov\nNov\nNov\nNov\nNov\nNov\nNov\nNov\n26 26 26 272727 2727 28 28 28 2828\nTUE\nNov\nTUE\nWED\nWED\nWED\nWED\nWED\nMON\nMON\nMON\nTUE\nTUE\nTUE\n1:30 PM\n3:00 PM\n3:00 PM\n4:30 PM\n4:30 PM 9:30 AM\n6:00 PM11:00 AM\n11:00 AM\n12:30 PM\n1:30 PM\n3:00 PM\n3:00 PM\n4:30 PM\n4:30 PM 9:30 AM\n6:00 PM11:00 AM\n11:00 AM\n12:30 PM\n1:30 PM\n3:00 PM\n3:00 PM\n4:30 PM\n4:30 PM\n6:00 PM\n1 participant\nUnsubscribe from updates\nNO COMMENTS\n",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 66,
                                    "y": 36
                                },
                                {
                                    "x": 1471,
                                    "y": 36
                                },
                                {
                                    "x": 1471,
                                    "y": 852
                                },
                                {
                                    "x": 66,
                                    "y": 852
                                }
                            ]
                        }
                    },
                    {
                        "description": "Regular",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 409,
                                    "y": 38
                                },
                                {
                                    "x": 582,
                                    "y": 38
                                },
                                {
                                    "x": 582,
                                    "y": 87
                                },
                                {
                                    "x": 409,
                                    "y": 87
                                }
                            ]
                        }
                    },
                    {
                        "description": "Meeting",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 594,
                                    "y": 36
                                },
                                {
                                    "x": 773,
                                    "y": 36
                                },
                                {
                                    "x": 773,
                                    "y": 87
                                },
                                {
                                    "x": 594,
                                    "y": 87
                                }
                            ]
                        }
                    },
                    {
                        "description": "Django-Project",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 789,
                                    "y": 40
                                },
                                {
                                    "x": 1125,
                                    "y": 40
                                },
                                {
                                    "x": 1125,
                                    "y": 87
                                },
                                {
                                    "x": 789,
                                    "y": 87
                                }
                            ]
                        }
                    },
                    {
                        "description": "by",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 615,
                                    "y": 96
                                },
                                {
                                    "x": 631,
                                    "y": 96
                                },
                                {
                                    "x": 631,
                                    "y": 116
                                },
                                {
                                    "x": 615,
                                    "y": 116
                                }
                            ]
                        }
                    },
                    {
                        "description": "Arne",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 640,
                                    "y": 96
                                },
                                {
                                    "x": 679,
                                    "y": 96
                                },
                                {
                                    "x": 679,
                                    "y": 116
                                },
                                {
                                    "x": 640,
                                    "y": 116
                                }
                            ]
                        }
                    },
                    {
                        "description": "Zerndt",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 687,
                                    "y": 96
                                },
                                {
                                    "x": 744,
                                    "y": 96
                                },
                                {
                                    "x": 744,
                                    "y": 116
                                },
                                {
                                    "x": 687,
                                    "y": 116
                                }
                            ]
                        }
                    },
                    {
                        "description": "7",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 762,
                                    "y": 96
                                },
                                {
                                    "x": 769,
                                    "y": 96
                                },
                                {
                                    "x": 769,
                                    "y": 116
                                },
                                {
                                    "x": 762,
                                    "y": 116
                                }
                            ]
                        }
                    },
                    {
                        "description": "days",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 777,
                                    "y": 96
                                },
                                {
                                    "x": 816,
                                    "y": 96
                                },
                                {
                                    "x": 816,
                                    "y": 116
                                },
                                {
                                    "x": 777,
                                    "y": 116
                                }
                            ]
                        }
                    },
                    {
                        "description": "ago",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 824,
                                    "y": 96
                                },
                                {
                                    "x": 852,
                                    "y": 96
                                },
                                {
                                    "x": 852,
                                    "y": 116
                                },
                                {
                                    "x": 824,
                                    "y": 116
                                }
                            ]
                        }
                    },
                    {
                        "description": "Print",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 871,
                                    "y": 96
                                },
                                {
                                    "x": 913,
                                    "y": 96
                                },
                                {
                                    "x": 913,
                                    "y": 116
                                },
                                {
                                    "x": 871,
                                    "y": 116
                                }
                            ]
                        }
                    },
                    {
                        "description": "O",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 371,
                                    "y": 228
                                },
                                {
                                    "x": 391,
                                    "y": 228
                                },
                                {
                                    "x": 391,
                                    "y": 248
                                },
                                {
                                    "x": 371,
                                    "y": 248
                                }
                            ]
                        }
                    },
                    {
                        "description": "All",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 413,
                                    "y": 229
                                },
                                {
                                    "x": 435,
                                    "y": 229
                                },
                                {
                                    "x": 435,
                                    "y": 245
                                },
                                {
                                    "x": 413,
                                    "y": 245
                                }
                            ]
                        }
                    },
                    {
                        "description": "times",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 441,
                                    "y": 229
                                },
                                {
                                    "x": 491,
                                    "y": 229
                                },
                                {
                                    "x": 491,
                                    "y": 245
                                },
                                {
                                    "x": 441,
                                    "y": 245
                                }
                            ]
                        }
                    },
                    {
                        "description": "displayed",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 498,
                                    "y": 229
                                },
                                {
                                    "x": 580,
                                    "y": 229
                                },
                                {
                                    "x": 580,
                                    "y": 248
                                },
                                {
                                    "x": 498,
                                    "y": 248
                                }
                            ]
                        }
                    },
                    {
                        "description": "in",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 588,
                                    "y": 234
                                },
                                {
                                    "x": 606,
                                    "y": 234
                                },
                                {
                                    "x": 606,
                                    "y": 245
                                },
                                {
                                    "x": 588,
                                    "y": 245
                                }
                            ]
                        }
                    },
                    {
                        "description": "Europe/Berlin",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 615,
                                    "y": 230
                                },
                                {
                                    "x": 741,
                                    "y": 230
                                },
                                {
                                    "x": 741,
                                    "y": 249
                                },
                                {
                                    "x": 615,
                                    "y": 249
                                }
                            ]
                        }
                    },
                    {
                        "description": "Tick",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 413,
                                    "y": 299
                                },
                                {
                                    "x": 449,
                                    "y": 299
                                },
                                {
                                    "x": 449,
                                    "y": 315
                                },
                                {
                                    "x": 413,
                                    "y": 315
                                }
                            ]
                        }
                    },
                    {
                        "description": "the",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 454,
                                    "y": 300
                                },
                                {
                                    "x": 483,
                                    "y": 300
                                },
                                {
                                    "x": 483,
                                    "y": 315
                                },
                                {
                                    "x": 454,
                                    "y": 315
                                }
                            ]
                        }
                    },
                    {
                        "description": "checkboxes",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 489,
                                    "y": 300
                                },
                                {
                                    "x": 592,
                                    "y": 300
                                },
                                {
                                    "x": 592,
                                    "y": 315
                                },
                                {
                                    "x": 489,
                                    "y": 315
                                }
                            ]
                        }
                    },
                    {
                        "description": "twice",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 597,
                                    "y": 300
                                },
                                {
                                    "x": 643,
                                    "y": 300
                                },
                                {
                                    "x": 643,
                                    "y": 315
                                },
                                {
                                    "x": 597,
                                    "y": 315
                                }
                            ]
                        }
                    },
                    {
                        "description": "to",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 649,
                                    "y": 302
                                },
                                {
                                    "x": 666,
                                    "y": 302
                                },
                                {
                                    "x": 666,
                                    "y": 315
                                },
                                {
                                    "x": 649,
                                    "y": 315
                                }
                            ]
                        }
                    },
                    {
                        "description": "select",
                        "boundingPoly": {
                            "vertices": [
                                {
                                    "x": 673,
                                    "y": 300
                                },
                                {
                                    "x": 724,
                                    "y": 300
                                },
                                {
                                    "x": 724,
                                    "y": 315
                                },
                                {
                                    "x": 673,
                                    "y": 315
                                }
                            ]
                        }
                    },
                ],
                "fullTextAnnotation": {}
            }
        ]
    }
