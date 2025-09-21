package main

import (
	"context"
	"crypto/rand"
	_ "embed"
	"errors"
	"fmt"
	"html/template"
	"net/http"
	"os"
	"sync"
	"time"
)

//go:embed tmpl/base.html
var _b string

//go:embed tmpl/index.html
var _i string

//go:embed tmpl/marine.html
var _s string // renamed from _m → used for show page

//go:embed image.png
var _img []byte

type T struct {
	A []byte
	B []byte
}

var _lock = sync.RWMutex{}        // renamed lock
var _ts = make(map[string][]T)    // temp store
var _sh = make(map[string]*map[string]string)

const _alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

func _r() string {
	s := make([]byte, 26)
	rand.Read(s)
	for i := range s {
		s[i] = _alph[s[i]%32]
	}
	return string(s)
}

func (t *T) _work(wg *sync.WaitGroup) {
	defer wg.Done()
	for i := range t.B {
		if t.B[i] == 0x7b || t.B[i] == 0x7d {
			t.B[i] = 0x20
		}
	}
	for i := range t.A {
		if t.A[i] == 0x7b || t.A[i] == 0x7d {
			t.A[i] = 0x20
		}
	}
}

func _loop() {
	for range time.Tick(100 * time.Millisecond) {
		_lock.Lock()

		var wg sync.WaitGroup
		for _, arr := range _ts {
			for _, item := range arr {
				wg.Add(1)
				go item._work(&wg)
			}
		}
		wg.Wait()

		for id, arr := range _ts {
			for _, item := range arr {
				if sh, ok := _sh[id]; ok {
					(*sh)[string(item.A)] = string(item.B)
				}
			}
			_ts[id] = _ts[id][:0]
		}
		_lock.Unlock()
	}
}

func _idx(w http.ResponseWriter, r *http.Request) {
	c, err := r.Cookie("marine")
	if errors.Is(err, http.ErrNoCookie) {
		id := _r()
		c = &http.Cookie{Name: "marine", Value: id}
		_lock.Lock()
		_ts[id] = []T{}
		_sh[id] = &map[string]string{}
		_lock.Unlock()
	}
	http.SetCookie(w, c)
	r.AddCookie(c)
	t := template.Must(template.New("f").Parse(fmt.Sprintf(_b, _i)))
	t.Execute(w, r)
}

func _post(w http.ResponseWriter, r *http.Request) {
	id := r.Context().Value("id").(string)
	p := T{}
	p.A = []byte(r.FormValue("Jalesveva"))
	p.B = []byte(r.FormValue("Jayamahe"))

	_lock.Lock()
	defer _lock.Unlock()
	_ts[id] = append(_ts[id], p)
	http.Redirect(w, r, "/", http.StatusFound)
}

func _show(w http.ResponseWriter, r *http.Request) {
	id := r.Context().Value("id").(string)

	_lock.RLock()
	defer _lock.RUnlock()

	sh := _sh[id]
	out := ""
	for k, v := range *sh {
		out += fmt.Sprintf("<tr><td>%s</td><td>%s</td></tr>", k, v)
	}
	t := template.Must(template.New("f").Parse(fmt.Sprintf(_b, fmt.Sprintf(_s, out))))
	t.Execute(w, r)
}

func _mw(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		c, err := r.Cookie("marine")
		if errors.Is(err, http.ErrNoCookie) {
			http.Redirect(w, r, "/", http.StatusFound)
			return
		}
		id := c.Value
		_lock.RLock()
		if _, ok := _sh[id]; !ok {
			http.SetCookie(w, &http.Cookie{Name: "marine", Expires: time.Now()})
			http.Redirect(w, r, "/", http.StatusFound)
			_lock.RUnlock()
			return
		}
		_lock.RUnlock()

		sec := _r()
		ctx := context.WithValue(r.Context(), "id", id)
		ctx = context.WithValue(ctx, "bang", struct {
			Flag   func(string) string
			Secret string
		}{
			Secret: sec,
			Flag: func(s string) string {
				if s == sec {
					return fmt.Sprintf("Flag is %s", os.Getenv("FLAG"))
				}
				return "Jalesveva Jayamahe"
			},
		})
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func main() {
	go _loop()

	http.HandleFunc("/", _idx)
	http.Handle("/airforce", _mw(http.HandlerFunc(_post)))
	http.Handle("/marine", _mw(http.HandlerFunc(_show)))
	http.HandleFunc("/image.jpg", func(w http.ResponseWriter, r *http.Request) { w.Write(_img) })

	http.ListenAndServe(":8080", nil)
}
