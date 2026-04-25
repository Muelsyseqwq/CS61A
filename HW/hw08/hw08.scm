(define (ascending? s) (if (null? s) #t (if (null? (cdr s)) #t (if (> (car s) (car (cdr s))) #f  (ascending? (cdr s))  ))))

(define (my-filter pred s) (if (null? s) '() (if (pred (car s)) (cons(car s) (my-filter pred (cdr s)))  (my-filter pred (cdr s)))))

(define (interleave lst1 lst2)(cond ((and (null? lst1) (null? lst2)) '())
                                          ((null? lst1) lst2)
                                          ((null? lst2) lst1)
                                (else (cons (car lst1) (interleave lst2 (cdr lst1))))
                                          )
                                 )

(define (no-repeats s)
  (if (null? s) '() (cons (car s) (no-repeats (filter (lambda (x)  (not (= x (car s)))) s )  )  )))

