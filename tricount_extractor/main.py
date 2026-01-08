from tricount_extractor.parse_args import parse_args
from tricount_extractor.client.client import TricountClient
from tricount_extractor.models.registry import Registry
from tricount_extractor.saver import RegistrySaver


class Processor:
    def process(self, registry_ids: list[str], folder: str) -> None:
        errors = self._process(registry_ids, folder)
        if len(errors) == 0:
            return
        raise ExceptionGroup("failed to process some tricounts", errors)

    @staticmethod
    def _process(registry_ids: list[str], folder: str) -> list[Exception]:
        errors = []
        with TricountClient() as client:
            for registry_id in registry_ids:
                try:
                    response = client.get_registry(registry_id)
                    response_data = response.json()
                    registry = Registry.from_json(response_data)
                    saved_path = RegistrySaver().save(registry, folder)
                    print(f"registry ID '{registry_id}' saved '{saved_path}'")
                except Exception as e:
                    error = Exception(f"failed to process tricount {registry_id}: {e}")
                    error.__cause__ = e
                    errors.append(error)
        return errors


def main() -> None:
    args = parse_args()

    try:
        Processor().process(args.registry_id, args.folder)
    except Exception:
        print("error occured while processing registries.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
