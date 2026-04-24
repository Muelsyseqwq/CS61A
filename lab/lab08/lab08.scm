(define (over-or-under num1 num2) (cond ((< num1 num2) -1) ((= num1 num2) 0) ((> num1 num2) 1)))

(define (composed f g) (lambda (x) (f (g x))))

(define (repeat f n)  (if (= n 1) f  (composed f (repeat f (- n 1)))))

(define (max a b)
  (if (> a b)
      a
      b))

(define (min a b)
  (if (> a b)
      b
      a))

(define (gcd a b) (if (zero? (modulo (max a b) (min a b))) (min a b)  (gcd (min a b) (modulo (max a b) (min a b)))))

(define (exp b n)
  (define (helper n so-far) (if (zero? n) so-far (helper (- n 1) (* b so-far))))
  (helper n 1))

(define (swap s)
  (define (helper sofar rest) (cond ((null? rest) sofar) ((null? (cdr rest)) (append sofar (list (car rest)))) (else (helper (append sofar (list (car (cdr rest)) (car rest))) (cdr (cdr rest)))))

                                )
    (helper () s)
  )

;(define (make-adder num) (define (add x) (+ num x)) add)
(define (make-adder num) (lambda (x) (+ num x)))