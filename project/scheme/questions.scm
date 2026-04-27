(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cadar x) (car (cdr (car x))))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

;; Problem 14
;; Returns a list of two-element lists
(define (enumerate s)
  ; BEGIN PROBLEM 14
  (define (helper lst index)
    (if (null? lst) '()
                 (cons (list index (car lst)) (helper (cdr lst) (+ index 1))
                         )))
                       (helper s 0)
                   ; END PROBLEM 14


  )


;; Problem 15

;; Return the value for a key in a dictionary list
(define (get dict key)
  ; BEGIN PROBLEM 15
  (if (null? dict) #f
  (if (equal? (caar dict) key) (cadar dict)  (get (cdr dict) key)   )
  ; END PROBLEM 15
  ))

;; Return a dictionary list with a (key value) pair
(define (set dict key val)
  ; BEGIN PROBLEM 15
  (define (helper dict key val)
    (if (null? dict) (list(list key val))
    (if (equal? (caar dict) key)  (cons (list key val) (cdr dict))  (cons (car dict) (helper (cdr dict ) key val)   )    )   )     )
  ; END PROBLEM 15
  (helper dict key val)
  )

;; Problem 16

;; implement solution-code
(define (solution-code problem solution)
  ; BEGIN PROBLEM 16
  (cond ((null? problem) '())
    ((equal? problem '_____) solution)
  ((not(pair? problem)) problem)
  (else (cons(solution-code (car problem) solution) (solution-code (cdr problem) solution))  ) )
  ; END PROBLEM 16
)
