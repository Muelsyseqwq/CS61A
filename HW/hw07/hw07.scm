(define (square n) (* n n))

(define (pow base exp) (if (zero? exp) 1  (if (even? exp) (square (pow base (/ exp 2))) (* base (pow base (- exp 1))))))

(define (repeatedly-cube n x)
  (if (zero? n)
      x
      (begin (define y (pow x 3)) (repeatedly-cube (- n 1) y))))

(define (cddr s) (cdr (cdr s)))

(define (cadr s) (car (cdr s)))

(define (caddr s) (car (cddr s)))
