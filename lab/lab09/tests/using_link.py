test = {
  'name': 'using-link',
  'points': 0,
  'suites': [
    {
      'cases': [
        {
          'answer': "Link('+', Link(Link('-', Link(2, Link(4))), Link(6, Link(8))))",
          'choices': [
            "Link('+', Link('-', Link(2, Link(4, Link(6, Link(8))))))",
            "Link('+', Link(Link(-, Link(2, Link(4))), Link(6, Link(8))))",
            'Link(+, Link(Link(-, Link(2, Link(4))), Link(6, Link(8))))',
            "Link('+', Link(Link('-', Link(2, Link(4))), Link(6, Link(8))))",
            'None of these'
          ],
          'hidden': False,
          'locked': False,
          'multiline': False,
          'question': 'Find the Python expression that returns a `Link` representing the given expression: (+ (- 2 4) 6 8)'
        },
        {
          'answer': '+',
          'choices': [
            '-',
            '+',
            '(',
            '2',
            '6',
            'None of these'
          ],
          'hidden': False,
          'locked': False,
          'multiline': False,
          'question': "What is the operator of the previous part's call expression?"
        },
        {
          'answer': 'p.first',
          'choices': [
            'p',
            'p.first',
            'p.rest',
            'p.rest.first',
            'p.first.rest'
          ],
          'hidden': False,
          'locked': False,
          'multiline': False,
          'question': r"""
          If the `Link` you constructed in the previous part was bound to the name `p`,
          how would you retrieve the operator?
          """
        },
        {
          'answer': 'p.rest',
          'choices': [
            'p',
            'p.first',
            'p.rest',
            'p.rest.first',
            'p.first.rest'
          ],
          'hidden': False,
          'locked': False,
          'multiline': False,
          'question': r"""
          If the `Link` you constructed was bound to the name `p`, 
          how would you retrieve a list containing all of the operands?
          """
        },
        {
          'answer': 'p.rest.first',
          'choices': [
            'p',
            'p.first',
            'p.rest',
            'p.rest.first',
            'p.first.rest'
          ],
          'hidden': False,
          'locked': False,
          'multiline': False,
          'question': 'How would you retrieve only the first operand?'
        },
        {
          'answer': "Link('-', Link(2, Link(4)))",
          'choices': [
            "'-'",
            "'+'",
            '2',
            '4',
            '-2',
            "Link('-', Link(2, Link(4)))",
            'Link(2, Link(4))'
          ],
          'hidden': False,
          'locked': False,
          'multiline': False,
          'question': 'What is the first operand of the call expression (+ (- 2 4) 6 8) prior to evaluation?'
        }
      ],
      'scored': False,
      'type': 'concept'
    }
  ]
}
