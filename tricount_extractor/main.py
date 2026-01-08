import httpx

from tricount_extractor.parse_args import parse_args
from tricount_extractor.client.client import TricountClient
from tricount_extractor.models.registry import Registry
from tricount_extractor.saver import RegistrySaver


class Processor:
    def process(
        self,
        registry_ids: list[str],
        folder: str,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        errors = self._process(registry_ids, folder, transport=transport)
        if len(errors) == 0:
            return
        raise ExceptionGroup("failed to process some tricounts", errors)

    def _process(
        self,
        registry_ids: list[str],
        folder: str,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> list[Exception]:
        errors = []
        with TricountClient(transport=transport) as client:
            for registry_id in registry_ids:
                error = self._process_registry_id(client, registry_id, folder)
                if error is None:
                    continue
                errors.append(error)
        return errors

    @staticmethod
    def _process_registry_id(
        client: TricountClient, registry_id: str, folder: str
    ) -> None | Exception:
        try:
            response = client.get_registry(registry_id)
            response_data = response.json()
            registry = Registry.from_json(response_data)
            saved_path = RegistrySaver().save(registry, folder)
            print(f"registry ID '{registry_id}' saved '{saved_path}'")
            return None
        except Exception as e:
            error = Exception(f"failed to process tricount {registry_id}: {e}")
            error.__cause__ = e
            return error


def main() -> None:
    args = parse_args()

    try:
        Processor().process(args.registry_id, args.folder)
    except ExceptionGroup as exc:
        print(f"error occured while processing registries: {exc.exceptions}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
