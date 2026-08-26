# Generics

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.5 — 1. Programming mastery

## Problem

உங்களுக்கு 5 domain entities இருக்கு: User, Order, Payment, Product, Invoice. எல்லாத்துக்கும் `findById`, `findAll`, `save`, `delete` மாதிரி same CRUD logic தேவை.

இப்போது நீங்கள் என்ன செய்வீர்கள்?

Option A: ஒவ்வொரு entity-க்கும் தனித்தனி Repository class எழுதுவது. Code copy-paste, 80% same.

Option B: `Object` அல்லது `Map<String,Object>` use பண்ணி ஒரே generic class எழுதி, எல்லா இடத்திலும் cast பண்ணுவது. Runtime-ல `ClassCastException` வரும்.

இது painful ஆகிறது. Duplicate code வளரும், bug fix ஒரு இடத்தில் பண்ணினால் மற்ற இடங்களில் மறந்து விடும். Type safety இல்லாமல் run-time error வரும்.

**Problem ஆனது:** Reuse வேண்டும், ஆனால் type safety கூட வேண்டும். Code duplication வேண்டாம், ஆனால் compiler-க்கு type தெரிய வேண்டும்.

## Mental Model

Generics என்பது ஒரு blueprint-ஐ எழுதி, அதை compile time-ல எந்த type-க்கு பயன்படுத்துவது என்று சொல்லும் mechanism.

நினைத்துக் கொள்ளுங்கள்: `List<T>` என்பது ஒரு container. T என்பது placeholder. நீங்கள் `List<String>` என்று சொன்னால் compiler அந்த placeholder-ஐ String-க்கு bind பண்ணி, அதற்கேற்ற type checks போடும்.

ஒரே implementation, பல types. ஒரே தர்க்கம், வெவ்வேறு data.

## How It Works

நீங்கள் type parameter `<T>` define பண்ணுகிறீர்கள். Compiler அதை எல்லா இடத்திலும் substitute பண்ணி, type safety enforce பண்ணுகிறது.

Java-ல:

```java
class Repository<T, ID> {
    T findById(ID id);
    List<T> findAll();
    void save(T entity);
}
```

பயன்பாடு:
```java
Repository<User, Long> userRepo = new Repository<>();
Repository<Order, String> orderRepo = new Repository<>();
```

TypeScript-ல:
```ts
function map<T, U>(arr: T[], fn: (x: T) => U): U[] {
  return arr.map(fn);
}
```

Compile time-ல T என்பது என்ன என்று தெரிந்துவிடும். Runtime-ல Java-ல type erasure ஆகிவிடும், ஆனால் compiler உங்களுக்காக check பண்ணிவிட்டது.

## Architectural Reasoning

Generics useful ஆகிறது எப்போது?

* **Reusable abstractions** தேவைப்படும்போது. Pagination, sorting, caching, validation pipeline போன்ற cross-cutting logic.
* **API surface குறைக்க வேண்டும்போது.** ஒரே generic wrapper `ApiResponse<T>` உங்கள் எல்லா service-க்கும் போதும்.
* **Type safety + DRY** இரண்டும் வேண்டும்போது.

Alternatives:
* Duplicate code per type. Simple, but maintenance nightmare.
* `Object` + casting. DRY ஆனால் unsafe, runtime failure.
* Code generation. Works, but build complexity அதிகம்.

Architect ஆக நீங்கள் தேர்வு செய்யும்போது கேள்வி: இந்த abstraction எத்தனை இடத்தில் reuse ஆகும்? அதன் complexity justify செய்கிறதா?

## Trade-offs

* **Readability vs Reuse.** Generic code படிக்க கடினம். `<T extends Entity<ID> & Auditable>` மாதிரி bounds சேர்த்தால் learning curve அத
