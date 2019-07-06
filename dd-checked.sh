if [ -z "$2" ] ; then
  echo 'Usage: dd-checked.sh IMAGE TARGET' ;
  exit 1 ;
fi

IMAGE="$1"
TARGET="$2"
IMAGE_SIZE=$(stat -c%s "$IMAGE")
BLOCKS=$(expr $IMAGE_SIZE / 4096)

# Exit immediately if these commands fail
set -e

echo "Writing $IMAGE to $TARGET with 4K block size..."
dd if="$IMAGE" of="$TARGET" bs=4K

echo "Waiting for write operations to sync (this may take a while with slower media)..."
sync

set +e

dd if="$TARGET" bs=4K count=$(expr $BLOCKS + 1) status=none | head -c $IMAGE_SIZE | diff $IMAGE -

if [ $? != 0 ] ; then
  echo 'The image written DIFFERS from the original file :(' ;
else
  echo 'The image written is IDENTICAL to the original file :)' ;
fi
