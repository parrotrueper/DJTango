import QtQuick 2.15

Item {
    id: root
    property url source: ""
    property color tint: "white"
    property int iconWidth: 24
    property int iconHeight: 24

    width: iconWidth
    height: iconHeight

    Image {
        id: sourceImage
        source: root.source
        width: root.width
        height: root.height
        fillMode: Image.PreserveAspectFit
        smooth: true
        visible: false
    }

    ShaderEffectSource {
        id: sourceItem
        sourceItem: sourceImage
        hideSource: true
        live: true
        width: root.width
        height: root.height
    }

    ShaderEffect {
        anchors.fill: parent
        property variant source: sourceItem
        property color tintColor: root.tint
        fragmentShader: "\n" +
            "uniform lowp sampler2D source;\n" +
            "uniform lowp vec4 tintColor;\n" +
            "varying highp vec2 qt_TexCoord0;\n" +
            "void main() {\n" +
            "    lowp vec4 c = texture2D(source, qt_TexCoord0);\n" +
            "    gl_FragColor = vec4(tintColor.rgb, c.a * tintColor.a);\n" +
            "}\n"
    }
}
