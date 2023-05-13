#include <assert.h>

#include <cstdint>
#include <iostream>
#include <vector>
#define a uint64_t
#define b index
#define c size
#define d hash
#define e hash_
#define f offset
#define g map
#define h Find
#define j return
#define k const
#define l int
#define m FlatHashMap
#define n values_
#define o Insert
#define p std::cout
#define q class
#define r Clear
#define s void
#define t while
#define u if
#define v nullptr
#define w value
#define x std::vector
#define y multiline_string
#define z assert

template<q T,a c>
q m{
public:
m(){
static_assert((c&(c-1))==0&&"Size must be a power of 2.");
r();
}

s r(){
for(a i=0;i<c;++i){
e[i]=a(-1);
}
}

T*h(a d){
a b=H(d)&(c-1);
a f=0;
t(f<c){
u(e[b]==-1ULL){
j v;
}
u(e[b]==d){
j&n[b];
}
f+=1;
b+=f;
b&=(c-1);
}
j v;
}

s o(a d,k T&w){
a b=H(d)&(c-1);
a f=0;
t(e[b]!=-1ULL){
f+=1;
b+=f;
b&=(c-1);
}
e[b]=d;
n[b]=w;
}

private:
a H(a d)k{j d^(reinterpret_cast<a>(e)>>12);}

a e[c];
T n[c];
};

l main(){
x<x<l>>vec;m<l,32>g;

g.o(0,10);
g.o(1,15);

k l X=1'000'000'000;
k std::string y=
"aaaaa"
"bbbbb";

p<<y<<"\n";
p<<*g.h(0)<<"\n";
p<<*g.h(1)<<"\n";

z(*g.h(0)==10);
z(*g.h(1)==15);
}
