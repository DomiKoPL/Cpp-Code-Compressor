#include <assert.h>

#include <cstdint>
#include <iostream>
#include <vector>

template <class T, uint64_t size>
class FlatHashMap {
 public:
  FlatHashMap() {
    static_assert((size & (size - 1)) == 0 && "Size must be a power of 2.");
    Clear();
  }

  void Clear() {
    for (uint64_t i = 0; i < size; ++i) {
      hash_[i] = uint64_t(-1);
    }
  }

  T* Find(uint64_t hash) {
    uint64_t index = H(hash) & (size - 1);
    uint64_t offset = 0;
    while (offset < size) {
      if (hash_[index] == -1ULL) {
        return nullptr;
      }
      if (hash_[index] == hash) {
        return &values_[index];
      }
      offset += 1;
      index += offset;
      index &= (size - 1);
    }
    return nullptr;
  }

  void Insert(uint64_t hash, const T& value) {
    uint64_t index = H(hash) & (size - 1);
    uint64_t offset = 0;
    while (hash_[index] != -1ULL) {
      offset += 1;
      index += offset;
      index &= (size - 1);
    }
    hash_[index] = hash;
    values_[index] = value;
  }

 private:
  uint64_t H(uint64_t hash) const { return hash ^ (reinterpret_cast<uint64_t>(hash_) >> 12); }

  uint64_t hash_[size];
  T values_[size];
};

int main() {
  // Random comment.
  std::vector<std::vector<int>> vec;  // Another random comment.
  FlatHashMap<int, 32> map;

  map.Insert(0, 10);
  map.Insert(1, 15);

  const int X = 1'000'000'000;
  const std::string multiline_string =
      "aaaaa"
      "bbbbb";

  std::cout << multiline_string << "\n";
  std::cout << *map.Find(0) << "\n";
  std::cout << *map.Find(1) << "\n";

  assert(*map.Find(0) == 10);
  assert(*map.Find(1) == 15);
}
