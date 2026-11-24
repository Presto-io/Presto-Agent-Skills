#let data = json(sys.inputs.at("source"))
#set page(paper: "a4", margin: (top: 26mm, bottom: 27mm, left: 34mm, right: 29mm))
#set text(font: "STFangsong", size: 15pt, lang: "zh")
#set par(first-line-indent: (amount: 2em, all: true), justify: true, leading: 16pt)
#align(center, text(font: "Songti SC", size: 19pt, weight: "bold")[证 明])
#v(15mm)
#(data.before_name)#underline(data.student_name)#(data.after_name)

#v(44mm)
#align(right, block(width: 43mm)[
  #set par(first-line-indent: 0pt, justify: false, leading: 16pt)
  #align(center)[
    #(data.issuer) \
    #(data.issued_on)
  ]
])
