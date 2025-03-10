use super::*;
use polars_core::export::{
    _boost_hash_combine,
    ahash::{self, CallHasher},
    rayon::prelude::*,
};
use polars_core::utils::NoNull;
use std::hash::Hash;

fn hash_agg<T>(ca: &ChunkedArray<T>, random_state: &ahash::RandomState) -> u64
where
    T: PolarsIntegerType,
    T::Native: Hash + CallHasher,
{
    // Note that we don't use the no null branch! This can break in unexpected ways.
    // for instance with threading we split an array in n_threads, this may lead to
    // splits that have no nulls and splits that have nulls. Then one array is hashed with
    // Option<T> and the other array with T.
    // Meaning that they cannot be compared. By always hashing on Option<T> the random_state is
    // the only deterministic seed.

    // just some large prime
    let mut hash_agg = 9069731903u64;

    //  just some large prime
    let null_hash = 2413670057;

    ca.downcast_iter().for_each(|arr| {
        for opt_v in arr.iter() {
            match opt_v {
                Some(v) => {
                    let r = T::Native::get_hash(v, random_state);
                    hash_agg = _boost_hash_combine(hash_agg, r);
                }
                None => {
                    hash_agg = _boost_hash_combine(hash_agg, null_hash);
                }
            }
        }
    });
    hash_agg
}

pub(crate) fn hash(ca: &ListChunked, build_hasher: ahash::RandomState) -> UInt64Chunked {
    if !ca.inner_dtype().to_physical().is_numeric() {
        panic!(
            "Hashing a list with a non-numeric inner type not supported. Got dtype: {:?}",
            ca.dtype()
        );
    }

    // just some large prime
    let null_hash = 1969099309u64;

    let out: NoNull<UInt64Chunked> = ca
        .par_iter()
        .map(|opt_s: Option<Series>| match opt_s {
            None => null_hash,
            Some(s) => {
                let s = s.to_physical_repr();
                if s.bit_repr_is_large() {
                    let ca = s.bit_repr_large();
                    hash_agg(&ca, &build_hasher)
                } else {
                    let ca = s.bit_repr_small();
                    hash_agg(&ca, &build_hasher)
                }
            }
        })
        .collect();

    let mut out = out.into_inner();
    out.rename(ca.name());
    out
}
