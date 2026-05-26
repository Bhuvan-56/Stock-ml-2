import { fireEvent, render, screen } from "@testing-library/react";

import { DatePickerField } from "@/components/ui/date-picker-field";

describe("DatePickerField", () => {
  it("opens the calendar and selects a date", () => {
    const handleChange = vi.fn();

    render(
      <DatePickerField
        id="start-date"
        label="Start date"
        placeholder="Select start date"
        value="2024-05-10"
        onChange={handleChange}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Choose start date" }));
    fireEvent.click(screen.getByRole("button", { name: "May 14, 2024" }));

    expect(handleChange).toHaveBeenCalledWith("2024-05-14");
  });

  it("clears the selected date", () => {
    const handleChange = vi.fn();

    render(
      <DatePickerField
        id="end-date"
        label="End date"
        placeholder="Select end date"
        value="2024-06-01"
        onChange={handleChange}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Clear" }));

    expect(handleChange).toHaveBeenCalledWith("");
  });

  it("allows jumping directly to another year", () => {
    const handleChange = vi.fn();

    render(
      <DatePickerField
        id="start-date"
        label="Start date"
        placeholder="Select start date"
        value="2024-05-10"
        onChange={handleChange}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Choose start date" }));
    fireEvent.change(screen.getByLabelText("Select year for start date"), {
      target: { value: "2019" }
    });
    fireEvent.change(screen.getByLabelText("Select month for start date"), {
      target: { value: "0" }
    });
    fireEvent.click(screen.getByRole("button", { name: "January 15, 2019" }));

    expect(handleChange).toHaveBeenCalledWith("2019-01-15");
  });
});
