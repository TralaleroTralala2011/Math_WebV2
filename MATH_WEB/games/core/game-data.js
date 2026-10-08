/* =========================================================
   MATH WEB
   GAME DATA
   ========================================================= */

(function () {

    "use strict";


    /* =====================================================
       GAME DATA
    ===================================================== */

    const GAME_DATA = {

        probability: {
            id: 1,
            code: "PROBABILITY",
            name: "Xác suất",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện tập xác suất thông qua các tình huống bốc bi, xúc xắc và lựa chọn thực tế.",

            games: {

                marble: {
                    id: "marble",
                    code: "PROBABILITY_MARBLE",
                    name: "Bốc bi",
                    description:
                        "Tính xác suất thông qua những lượt bốc bi.",
                    icon: "🔮",
                    path:
                        "../../games/probability/marble.html"
                },

                dice: {
                    id: "dice",
                    code: "PROBABILITY_DICE",
                    name: "Xúc xắc",
                    description:
                        "Khám phá xác suất bằng các tình huống với xúc xắc.",
                    icon: "🎲",
                    path:
                        "../../games/probability/dice.html"
                },

                situation: {
                    id: "situation",
                    code: "PROBABILITY_SITUATION",
                    name: "Chọn tình huống",
                    description:
                        "Phân tích các tình huống thực tế và tìm xác suất.",
                    icon: "🧩",
                    path:
                        "../../games/probability/situation.html"
                }

            }
        },


        combination: {
            id: 2,
            code: "COMBINATION",
            name: "Tổ hợp",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện cách lựa chọn đối tượng mà không quan tâm đến thứ tự.",

            games: {

                team: {
                    id: "team",
                    code: "COMBINATION_TEAM",
                    name: "Chọn đội",
                    description:
                        "Lựa chọn các thành viên để tạo thành một đội.",
                    icon: "👥",
                    path:
                        "../../games/combination/team.html"
                },

                choice: {
                    id: "choice",
                    code: "COMBINATION_CHOICE",
                    name: "Ghép lựa chọn",
                    description:
                        "Ghép các lựa chọn phù hợp bằng tư duy tổ hợp.",
                    icon: "🧩",
                    path:
                        "../../games/combination/choice.html"
                },

                hunt: {
                    id: "hunt",
                    code: "COMBINATION_HUNT",
                    name: "Săn tổ hợp",
                    description:
                        "Tìm nhanh số cách lựa chọn trong các thử thách tổ hợp.",
                    icon: "🔎",
                    path:
                        "../../games/combination/hunt.html"
                }

            }
        },


        permutation: {
            id: 3,
            code: "PERMUTATION",
            name: "Chỉnh hợp",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện cách chọn và sắp xếp các phần tử khi thứ tự có ý nghĩa.",

            games: {

                position: {
                    id: "position",
                    code: "PERMUTATION_POSITION",
                    name: "Xếp vị trí",
                    description:
                        "Sắp xếp các đối tượng vào những vị trí khác nhau.",
                    icon: "📍",
                    path:
                        "../../games/permutation/position.html"
                },

                code: {
                    id: "code",
                    code: "PERMUTATION_CODE",
                    name: "Mật mã",
                    description:
                        "Tạo và giải các mật mã dựa trên quy tắc sắp xếp.",
                    icon: "🔐",
                    path:
                        "../../games/permutation/code.html"
                },

                order: {
                    id: "order",
                    code: "PERMUTATION_ORDER",
                    name: "Sắp thứ tự",
                    description:
                        "Tìm số cách sắp xếp các phần tử theo thứ tự khác nhau.",
                    icon: "📋",
                    path:
                        "../../games/permutation/order.html"
                }

            }
        },


        function: {
            id: 4,
            code: "FUNCTION",
            name: "Hàm số",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện đọc, tính toán và phân tích hàm số qua bảng giá trị và đồ thị.",

            games: {

                point: {
                    id: "point",
                    code: "FUNCTION_POINT",
                    name: "Bắt điểm",
                    description:
                        "Xác định và bắt đúng các điểm trên mặt phẳng tọa độ.",
                    icon: "🎯",
                    path:
                        "../../games/function/point.html"
                },

                intersection: {
                    id: "intersection",
                    code: "FUNCTION_INTERSECTION",
                    name: "Tìm giao điểm",
                    description:
                        "Tìm giao điểm của các đồ thị hàm số.",
                    icon: "✖️",
                    path:
                        "../../games/function/intersection.html"
                },

                graph: {
                    id: "graph",
                    code: "FUNCTION_GRAPH",
                    name: "Đồ thị bí ẩn",
                    description:
                        "Phân tích dữ kiện để nhận diện đồ thị phù hợp.",
                    icon: "📈",
                    path:
                        "../../games/function/graph.html"
                }

            }
        },


        systemEquation: {
            id: 5,
            code: "SYSTEM_EQUATION",
            name: "Hệ phương trình",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Giải và kiểm tra nghiệm của hệ phương trình bằng các phương pháp phù hợp.",

            games: {

                investigation: {
                    id: "investigation",
                    code: "SYSTEM_EQUATION_INVESTIGATION",
                    name: "Điều tra",
                    description:
                        "Tìm nghiệm thông qua các dữ kiện được cung cấp.",
                    icon: "🕵️",
                    path:
                        "../../games/system-equation/investigation.html"
                },

                value: {
                    id: "value",
                    code: "SYSTEM_EQUATION_VALUE",
                    name: "Tìm giá trị",
                    description:
                        "Tìm giá trị của các ẩn trong hệ phương trình.",
                    icon: "🔢",
                    path:
                        "../../games/system-equation/value.html"
                },

                match: {
                    id: "match",
                    code: "SYSTEM_EQUATION_MATCH",
                    name: "Ghép đáp án",
                    description:
                        "Ghép hệ phương trình với nghiệm tương ứng.",
                    icon: "🧩",
                    path:
                        "../../games/system-equation/match.html"
                }

            }
        },


        quadraticEquation: {
            id: 6,
            code: "QUADRATIC_EQUATION",
            name: "Phương trình bậc hai",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện giải phương trình bậc hai, tính biệt thức và xác định nghiệm.",

            games: {

                root: {
                    id: "root",
                    code: "QUADRATIC_EQUATION_ROOT",
                    name: "Săn nghiệm",
                    description:
                        "Tìm nghiệm chính xác của phương trình bậc hai.",
                    icon: "🎯",
                    path:
                        "../../games/quadratic-equation/root.html"
                },

                match: {
                    id: "match",
                    code: "QUADRATIC_EQUATION_MATCH",
                    name: "Ghép nghiệm",
                    description:
                        "Ghép phương trình với nghiệm tương ứng.",
                    icon: "🧩",
                    path:
                        "../../games/quadratic-equation/match.html"
                },

                unlock: {
                    id: "unlock",
                    code: "QUADRATIC_EQUATION_UNLOCK",
                    name: "Mở khóa",
                    description:
                        "Giải phương trình để mở khóa các thử thách tiếp theo.",
                    icon: "🔓",
                    path:
                        "../../games/quadratic-equation/unlock.html"
                }

            }
        },


        inequality: {
            id: 7,
            code: "INEQUALITY",
            name: "Bất phương trình",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện giải bất phương trình và biểu diễn tập nghiệm trên trục số.",

            games: {

                safeZone: {
                    id: "safeZone",
                    code: "INEQUALITY_SAFE_ZONE",
                    name: "Vùng an toàn",
                    description:
                        "Xác định vùng giá trị thỏa mãn bất phương trình.",
                    icon: "🛡️",
                    path:
                        "../../games/inequality/safe-zone.html"
                },

                interval: {
                    id: "interval",
                    code: "INEQUALITY_INTERVAL",
                    name: "Chọn khoảng",
                    description:
                        "Chọn khoảng nghiệm chính xác trên trục số.",
                    icon: "📏",
                    path:
                        "../../games/inequality/interval.html"
                },

                barrier: {
                    id: "barrier",
                    code: "INEQUALITY_BARRIER",
                    name: "Vượt rào",
                    description:
                        "Giải bất phương trình để vượt qua các thử thách.",
                    icon: "🚧",
                    path:
                        "../../games/inequality/barrier.html"
                }

            }
        },


        sequence: {
            id: 8,
            code: "SEQUENCE",
            name: "Dãy số",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Tìm quy luật, số hạng và mối quan hệ giữa các phần tử trong dãy số.",

            games: {

                rule: {
                    id: "rule",
                    code: "SEQUENCE_RULE",
                    name: "Tìm quy luật",
                    description:
                        "Phát hiện quy luật ẩn trong các dãy số.",
                    icon: "🔍",
                    path:
                        "../../games/sequence/rule.html"
                },

                fill: {
                    id: "fill",
                    code: "SEQUENCE_FILL",
                    name: "Điền số",
                    description:
                        "Điền số còn thiếu dựa trên quy luật của dãy.",
                    icon: "🔢",
                    path:
                        "../../games/sequence/fill.html"
                },

                race: {
                    id: "race",
                    code: "SEQUENCE_RACE",
                    name: "Đường đua dãy số",
                    description:
                        "Vượt qua các thử thách dãy số trong một cuộc đua.",
                    icon: "🏁",
                    path:
                        "../../games/sequence/race.html"
                }

            }
        },


        divisibility: {
            id: 9,
            code: "DIVISIBILITY",
            name: "Chia hết",
            category: "SỐ HỌC",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện nhận biết và vận dụng các dấu hiệu chia hết.",

            games: {

                find: {
                    id: "find",
                    code: "DIVISIBILITY_FIND",
                    name: "Truy tìm số",
                    description:
                        "Tìm những số thỏa mãn điều kiện chia hết.",
                    icon: "🔎",
                    path:
                        "../../games/divisibility/find.html"
                },

                select: {
                    id: "select",
                    code: "DIVISIBILITY_SELECT",
                    name: "Chọn số",
                    description:
                        "Chọn nhanh các số phù hợp với dấu hiệu chia hết.",
                    icon: "🎯",
                    path:
                        "../../games/divisibility/select.html"
                },

                unlock: {
                    id: "unlock",
                    code: "DIVISIBILITY_UNLOCK",
                    name: "Phá khóa",
                    description:
                        "Vận dụng dấu hiệu chia hết để phá khóa.",
                    icon: "🔐",
                    path:
                        "../../games/divisibility/unlock.html"
                }

            }
        },


        remainder: {
            id: 10,
            code: "REMAINDER",
            name: "Chia dư",
            category: "SỐ HỌC",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện xác định số dư và vận dụng quy tắc chia dư.",

            games: {

                draw: {
                    id: "draw",
                    code: "REMAINDER_DRAW",
                    name: "Bốc số",
                    description:
                        "Bốc số và xác định số dư tương ứng.",
                    icon: "🎱",
                    path:
                        "../../games/remainder/draw.html"
                },

                hunt: {
                    id: "hunt",
                    code: "REMAINDER_HUNT",
                    name: "Săn số dư",
                    description:
                        "Tìm số dư chính xác trong các thử thách số học.",
                    icon: "🔎",
                    path:
                        "../../games/remainder/hunt.html"
                },

                modulo: {
                    id: "modulo",
                    code: "REMAINDER_MODULO",
                    name: "Thử thách modulo",
                    description:
                        "Vận dụng phép modulo để giải các thử thách.",
                    icon: "%",
                    path:
                        "../../games/remainder/modulo.html"
                }

            }
        },


        radical: {
            id: 11,
            code: "RADICAL",
            name: "Căn thức",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện tính toán, rút gọn và biến đổi các biểu thức chứa căn thức.",

            games: {

                hunt: {
                    id: "hunt",
                    code: "RADICAL_HUNT",
                    name: "Săn căn",
                    description:
                        "Tìm và xử lý các biểu thức chứa căn.",
                    icon: "√",
                    path:
                        "../../games/radical/hunt.html"
                },

                simplify: {
                    id: "simplify",
                    code: "RADICAL_SIMPLIFY",
                    name: "Rút gọn nhanh",
                    description:
                        "Rút gọn biểu thức chứa căn một cách chính xác.",
                    icon: "⚡",
                    path:
                        "../../games/radical/simplify.html"
                },

                unlock: {
                    id: "unlock",
                    code: "RADICAL_UNLOCK",
                    name: "Mở khóa căn thức",
                    description:
                        "Giải các bài căn thức để mở khóa thử thách.",
                    icon: "🔓",
                    path:
                        "../../games/radical/unlock.html"
                }

            }
        },


        identities: {
            id: 12,
            code: "IDENTITIES",
            name: "Hằng đẳng thức",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Nhận biết và vận dụng các hằng đẳng thức đáng nhớ.",

            games: {

                match: {
                    id: "match",
                    code: "IDENTITIES_MATCH",
                    name: "Ghép công thức",
                    description:
                        "Ghép biểu thức với hằng đẳng thức tương ứng.",
                    icon: "🧩",
                    path:
                        "../../games/identities/match.html"
                },

                break: {
                    id: "break",
                    code: "IDENTITIES_BREAK",
                    name: "Phá biểu thức",
                    description:
                        "Phân tích biểu thức bằng các hằng đẳng thức.",
                    icon: "💥",
                    path:
                        "../../games/identities/break.html"
                },

                mystery: {
                    id: "mystery",
                    code: "IDENTITIES_MYSTERY",
                    name: "Công thức bí ẩn",
                    description:
                        "Khám phá hằng đẳng thức ẩn trong biểu thức.",
                    icon: "❓",
                    path:
                        "../../games/identities/mystery.html"
                }

            }
        },


        algebraicFraction: {
            id: 13,
            code: "ALGEBRAIC_FRACTION",
            name: "Phân thức đại số",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện tìm điều kiện xác định, rút gọn và thực hiện phép toán với phân thức đại số.",

            games: {

                simplify: {
                    id: "simplify",
                    code: "ALGEBRAIC_FRACTION_SIMPLIFY",
                    name: "Rút gọn",
                    description:
                        "Rút gọn các phân thức đại số.",
                    icon: "➗",
                    path:
                        "../../games/algebraic-fraction/simplify.html"
                },

                condition: {
                    id: "condition",
                    code: "ALGEBRAIC_FRACTION_CONDITION",
                    name: "Tìm điều kiện",
                    description:
                        "Tìm điều kiện xác định của phân thức.",
                    icon: "🔎",
                    path:
                        "../../games/algebraic-fraction/condition.html"
                },

                speed: {
                    id: "speed",
                    code: "ALGEBRAIC_FRACTION_SPEED",
                    name: "Phân thức tốc độ",
                    description:
                        "Giải nhanh các bài toán về phân thức đại số.",
                    icon: "⚡",
                    path:
                        "../../games/algebraic-fraction/speed.html"
                }

            }
        },


        geometry: {
            id: 14,
            code: "GEOMETRY",
            name: "Hình học",
            category: "HÌNH HỌC",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện nhận biết hình, tính góc, độ dài và giải quyết các tình huống hình học.",

            games: {

                angle: {
                    id: "angle",
                    code: "GEOMETRY_ANGLE",
                    name: "Tìm góc",
                    description:
                        "Tính và xác định các góc trong hình học.",
                    icon: "📐",
                    path:
                        "../../games/geometry/angle.html"
                },

                length: {
                    id: "length",
                    code: "GEOMETRY_LENGTH",
                    name: "Săn độ dài",
                    description:
                        "Tìm độ dài các đoạn thẳng trong những bài toán hình học.",
                    icon: "📏",
                    path:
                        "../../games/geometry/length.html"
                },

                map: {
                    id: "map",
                    code: "GEOMETRY_MAP",
                    name: "Bản đồ hình học",
                    description:
                        "Giải các thử thách hình học thông qua bản đồ.",
                    icon: "🗺️",
                    path:
                        "../../games/geometry/map.html"
                }

            }
        },


        statistics: {
            id: 15,
            code: "STATISTICS",
            name: "Thống kê",
            category: "THỐNG KÊ",
            level: "Cơ bản → Nâng cao",

            description:
                "Luyện đọc bảng số liệu, biểu đồ và phân tích thông tin thống kê.",

            games: {

                chart: {
                    id: "chart",
                    code: "STATISTICS_CHART",
                    name: "Đọc biểu đồ",
                    description:
                        "Đọc và phân tích thông tin từ các biểu đồ.",
                    icon: "📊",
                    path:
                        "../../games/statistics/chart.html"
                },

                data: {
                    id: "data",
                    code: "STATISTICS_DATA",
                    name: "Săn số liệu",
                    description:
                        "Tìm và phân tích các dữ liệu thống kê.",
                    icon: "🔎",
                    path:
                        "../../games/statistics/data.html"
                },

                challenge: {
                    id: "challenge",
                    code: "STATISTICS_CHALLENGE",
                    name: "Thử thách thống kê",
                    description:
                        "Vận dụng kiến thức thống kê để giải thử thách.",
                    icon: "🏆",
                    path:
                        "../../games/statistics/challenge.html"
                }

            }
        }

    };


    /* =====================================================
       VALIDATION
    ===================================================== */

    function isValidGame(
        game
    ) {

        if (
            !game ||
            typeof game !== "object"
        ) {
            return false;
        }

        return (
            typeof game.name === "string" &&
            game.name.trim() !== "" &&
            typeof game.path === "string" &&
            game.path.trim() !== ""
        );

    }


    function isValidTopic(
        topic
    ) {

        if (
            !topic ||
            typeof topic !== "object"
        ) {
            return false;
        }

        if (
            !Number.isInteger(
                topic.id
            ) ||
            topic.id <= 0
        ) {
            return false;
        }

        if (
            typeof topic.code !== "string" ||
            !topic.code.trim()
        ) {
            return false;
        }

        if (
            typeof topic.name !== "string" ||
            !topic.name.trim()
        ) {
            return false;
        }

        if (
            !topic.games ||
            typeof topic.games !== "object"
        ) {
            return false;
        }

        return true;

    }


    /* =====================================================
       TOPIC HELPERS
    ===================================================== */

    function getTopic(
        topicKey
    ) {

        if (
            typeof topicKey !== "string"
        ) {
            return null;
        }

        return (
            GAME_DATA[
                topicKey
            ] ||
            null
        );

    }


    function getTopicById(
        topicId
    ) {

        const id =
            Number(topicId);

        if (
            !Number.isInteger(id)
        ) {
            return null;
        }


        const topics =
            Object.values(
                GAME_DATA
            );


        return (
            topics.find(
                function (topic) {

                    return (
                        topic.id === id
                    );

                }
            ) ||
            null
        );

    }


    function getTopicByCode(
        code
    ) {

        if (
            typeof code !== "string"
        ) {
            return null;
        }


        const normalized =
            code
                .trim()
                .toUpperCase();


        if (!normalized) {
            return null;
        }


        const topics =
            Object.values(
                GAME_DATA
            );


        return (
            topics.find(
                function (topic) {

                    return (
                        topic.code ===
                        normalized
                    );

                }
            ) ||
            null
        );

    }


    /* =====================================================
       GAME HELPERS
    ===================================================== */

    function getGame(
        topicKey,
        gameKey
    ) {

        const topic =
            getTopic(
                topicKey
            );


        if (
            !topic ||
            typeof gameKey !== "string"
        ) {
            return null;
        }


        return (
            topic.games[
                gameKey
            ] ||
            null
        );

    }


    function getGameByCode(
        gameCode
    ) {

        if (
            typeof gameCode !== "string"
        ) {
            return null;
        }


        const normalized =
            gameCode
                .trim()
                .toUpperCase();


        if (!normalized) {
            return null;
        }


        const topics =
            Object.values(
                GAME_DATA
            );


        for (
            const topic of topics
        ) {

            const games =
                Object.values(
                    topic.games || {}
                );


            const game =
                games.find(
                    function (item) {

                        return (
                            item.code ===
                            normalized
                        );

                    }
                );


            if (game) {
                return game;
            }

        }


        return null;

    }


    function getAllTopics() {

        return Object.values(
            GAME_DATA
        );

    }


    function getAllGames() {

        const result = [];


        Object.values(
            GAME_DATA
        ).forEach(
            function (topic) {

                Object.values(
                    topic.games || {}
                ).forEach(
                    function (game) {

                        result.push(
                            {
                                ...game,

                                topicId:
                                    topic.id,

                                topicCode:
                                    topic.code,

                                topicName:
                                    topic.name

                            }
                        );

                    }
                );

            }
        );


        return result;

    }


    /* =====================================================
       STATISTICS
    ===================================================== */

    function getTopicCount() {

        return Object.keys(
            GAME_DATA
        ).length;

    }


    function getGameCount() {

        return getAllGames()
            .length;

    }


    function getGamesByTopic(
        topicKey
    ) {

        const topic =
            getTopic(
                topicKey
            );


        if (!topic) {
            return [];
        }


        return Object.values(
            topic.games || {}
        );

    }


    /* =====================================================
       SEARCH
    ===================================================== */

    function search(
        keyword
    ) {

        if (
            typeof keyword !== "string"
        ) {
            return [];
        }


        const query =
            keyword
                .trim()
                .toLowerCase();


        if (!query) {
            return [];
        }


        const results = [];


        Object.values(
            GAME_DATA
        ).forEach(
            function (topic) {

                const topicMatch =
                    topic.name
                        .toLowerCase()
                        .includes(query);


                Object.values(
                    topic.games || {}
                ).forEach(
                    function (game) {

                        const gameMatch =
                            game.name
                                .toLowerCase()
                                .includes(query) ||
                            game.code
                                .toLowerCase()
                                .includes(query);


                        if (
                            topicMatch ||
                            gameMatch
                        ) {

                            results.push(
                                {
                                    ...game,

                                    topicId:
                                        topic.id,

                                    topicCode:
                                        topic.code,

                                    topicName:
                                        topic.name
                                }
                            );

                        }

                    }
                );

            }
        );


        return results;

    }


    /* =====================================================
       FREEZE DATA
    ===================================================== */

    function deepFreeze(
        object
    ) {

        if (
            !object ||
            typeof object !== "object"
        ) {
            return object;
        }


        Object.freeze(
            object
        );


        Object.getOwnPropertyNames(
            object
        ).forEach(
            function (property) {

                const value =
                    object[property];


                if (
                    value &&
                    typeof value === "object" &&
                    !Object.isFrozen(value)
                ) {

                    deepFreeze(
                        value
                    );

                }

            }
        );


        return object;

    }


    deepFreeze(
        GAME_DATA
    );


    /* =====================================================
       PUBLIC API
    ===================================================== */

    window.GAME_DATA =
        GAME_DATA;

    window.MATHWEB_GAME_DATA = {

        data:
            GAME_DATA,

        getTopic:
            getTopic,

        getTopicById:
            getTopicById,

        getTopicByCode:
            getTopicByCode,

        getGame:
            getGame,

        getGameByCode:
            getGameByCode,

        getAllTopics:
            getAllTopics,

        getAllGames:
            getAllGames,

        getGamesByTopic:
            getGamesByTopic,

        search:
            search,

        getTopicCount:
            getTopicCount,

        getGameCount:
            getGameCount,

        isValidTopic:
            isValidTopic,

        isValidGame:
            isValidGame

    };


})();